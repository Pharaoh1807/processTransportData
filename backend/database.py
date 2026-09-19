import os
import json
import sqlite3
import uuid
import bcrypt
from datetime import datetime
from typing import Any, Dict, List, Optional
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load .env file (nếu tồn tại) trước khi đọc biến môi trường
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017").strip()
DATABASE_NAME = os.getenv("DATABASE_NAME", "transport_data_db")
SQLITE_DB_PATH = os.getenv(
    "SQLITE_DB_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "transport_data.db")
)


class MockResult:
    def __init__(self, inserted_id=None, matched_count=0, modified_count=0, deleted_count=0):
        self.inserted_id = inserted_id
        self.matched_count = matched_count
        self.modified_count = modified_count
        self.deleted_count = deleted_count


class SQLiteCursor:
    def __init__(self, items: List[Dict[str, Any]]):
        self.items = items
        self._iter = iter(items)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration:
            raise StopAsyncIteration

    async def to_list(self, length: Optional[int] = None) -> List[Dict[str, Any]]:
        if length is not None:
            return self.items[:length]
        return self.items


class SQLiteCollection:
    def __init__(self, conn: sqlite3.Connection, table_name: str):
        self.conn = conn
        self.table_name = table_name

    def _apply_projection(self, doc: Dict[str, Any], projection: Optional[Dict[str, int]]) -> Dict[str, Any]:
        if not projection:
            return doc
        d = dict(doc)
        for k, v in projection.items():
            if v == 0:
                d.pop(k, None)
        return d

    async def find_one(self, query: Dict[str, Any], projection: Optional[Dict[str, int]] = None) -> Optional[Dict[str, Any]]:
        if "_id" in query:
            cur = self.conn.execute(f"SELECT data FROM {self.table_name} WHERE id = ?", (str(query["_id"]),))
            row = cur.fetchone()
            if row:
                doc = json.loads(row[0])
                return self._apply_projection(doc, projection)
            return None

        if "email" in query and self.table_name == "users":
            cur = self.conn.execute(f"SELECT data FROM {self.table_name} WHERE email = ?", (query["email"].lower(),))
            row = cur.fetchone()
            if row:
                doc = json.loads(row[0])
                return self._apply_projection(doc, projection)
            return None

        cur = self.conn.execute(f"SELECT data FROM {self.table_name}")
        for (raw,) in cur:
            doc = json.loads(raw)
            if all(doc.get(k) == v for k, v in query.items()):
                return self._apply_projection(doc, projection)
        return None

    def find(self, query: Optional[Dict[str, Any]] = None, projection: Optional[Dict[str, int]] = None) -> SQLiteCursor:
        query = query or {}
        items = []

        if "file_id" in query and self.table_name == "records":
            cur = self.conn.execute("SELECT data FROM records WHERE file_id = ?", (str(query["file_id"]),))
            for (raw,) in cur:
                doc = json.loads(raw)
                items.append(self._apply_projection(doc, projection))
            return SQLiteCursor(items)

        if "user_id" in query and self.table_name == "files":
            cur = self.conn.execute("SELECT data FROM files WHERE user_id = ?", (str(query["user_id"]),))
            for (raw,) in cur:
                doc = json.loads(raw)
                items.append(self._apply_projection(doc, projection))
            return SQLiteCursor(items)

        cur = self.conn.execute(f"SELECT data FROM {self.table_name}")
        for (raw,) in cur:
            doc = json.loads(raw)
            if all(doc.get(k) == v for k, v in query.items()):
                items.append(self._apply_projection(doc, projection))
        return SQLiteCursor(items)

    async def insert_one(self, doc: Dict[str, Any]) -> MockResult:
        doc_id = str(doc.get("_id", uuid.uuid4()))
        doc["_id"] = doc_id
        raw_json = json.dumps(doc, default=str)

        if self.table_name == "users":
            email = str(doc.get("email", "")).lower()
            self.conn.execute(
                "INSERT OR REPLACE INTO users (id, email, data) VALUES (?, ?, ?)",
                (doc_id, email, raw_json)
            )
        elif self.table_name == "files":
            user_id = str(doc.get("user_id", ""))
            self.conn.execute(
                "INSERT OR REPLACE INTO files (id, user_id, data) VALUES (?, ?, ?)",
                (doc_id, user_id, raw_json)
            )
        elif self.table_name == "records":
            file_id = str(doc.get("file_id", ""))
            self.conn.execute(
                "INSERT INTO records (file_id, data) VALUES (?, ?)",
                (file_id, raw_json)
            )
        else:
            self.conn.execute(
                f"INSERT OR REPLACE INTO {self.table_name} (id, data) VALUES (?, ?)",
                (doc_id, raw_json)
            )
        self.conn.commit()
        return MockResult(inserted_id=doc_id)

    async def insert_many(self, docs: List[Dict[str, Any]]) -> MockResult:
        if not docs:
            return MockResult()
        if self.table_name == "records":
            batch = [(str(d.get("file_id", "")), json.dumps(d, default=str)) for d in docs]
            self.conn.executemany("INSERT INTO records (file_id, data) VALUES (?, ?)", batch)
        else:
            batch = [(str(d.get("_id", uuid.uuid4())), json.dumps(d, default=str)) for d in docs]
            self.conn.executemany(f"INSERT OR REPLACE INTO {self.table_name} (id, data) VALUES (?, ?)", batch)
        self.conn.commit()
        return MockResult()

    async def update_one(self, query: Dict[str, Any], update: Dict[str, Any]) -> MockResult:
        doc = await self.find_one(query)
        if not doc:
            return MockResult(matched_count=0, modified_count=0)
        set_vals = update.get("$set", {})
        doc.update(set_vals)
        doc_id = str(doc.get("_id", ""))
        raw_json = json.dumps(doc, default=str)

        if self.table_name == "users":
            self.conn.execute("UPDATE users SET data = ? WHERE id = ?", (raw_json, doc_id))
        elif self.table_name == "files":
            self.conn.execute("UPDATE files SET data = ? WHERE id = ?", (raw_json, doc_id))
        else:
            self.conn.execute(f"UPDATE {self.table_name} SET data = ? WHERE id = ?", (raw_json, doc_id))
        self.conn.commit()
        return MockResult(matched_count=1, modified_count=1)

    async def delete_one(self, query: Dict[str, Any]) -> MockResult:
        if "_id" in query:
            cur = self.conn.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (str(query["_id"]),))
            self.conn.commit()
            return MockResult(deleted_count=cur.rowcount)
        doc = await self.find_one(query)
        if doc:
            cur = self.conn.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (str(doc["_id"]),))
            self.conn.commit()
            return MockResult(deleted_count=cur.rowcount)
        return MockResult(deleted_count=0)

    async def delete_many(self, query: Dict[str, Any]) -> MockResult:
        if "file_id" in query and self.table_name == "records":
            cur = self.conn.execute("DELETE FROM records WHERE file_id = ?", (str(query["file_id"]),))
            self.conn.commit()
            return MockResult(deleted_count=cur.rowcount)
        if "user_id" in query and self.table_name == "files":
            cur = self.conn.execute("DELETE FROM files WHERE user_id = ?", (str(query["user_id"]),))
            self.conn.commit()
            return MockResult(deleted_count=cur.rowcount)

        docs = await self.find(query).to_list()
        cnt = 0
        for d in docs:
            r = await self.delete_one({"_id": d.get("_id")})
            cnt += r.deleted_count
        return MockResult(deleted_count=cnt)


class SQLiteDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_schema()
        self.users = SQLiteCollection(self.conn, "users")
        self.files = SQLiteCollection(self.conn, "files")
        self.records = SQLiteCollection(self.conn, "records")
        self._auto_seed_admin()

    def _init_schema(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE,
                data TEXT
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                data TEXT
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_files_user ON files(user_id)")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT,
                data TEXT
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_records_file ON records(file_id)")
        self.conn.commit()

    def _auto_seed_admin(self):
        """Seed default admin account if users table is empty."""
        cur = self.conn.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            admin_id = str(uuid.uuid4())
            admin_email = os.getenv("ADMIN_EMAIL", "admin@transport.com")
            admin_pass = os.getenv("ADMIN_PASSWORD", "admin123456")
            hashed_pass = bcrypt.hashpw(admin_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin_doc = {
                "_id": admin_id,
                "email": admin_email,
                "full_name": "System Administrator",
                "hashed_password": hashed_pass,
                "role": "admin",
                "is_approved": True,
                "created_at": datetime.now().isoformat()
            }
            self.conn.execute(
                "INSERT OR REPLACE INTO users (id, email, data) VALUES (?, ?, ?)",
                (admin_id, admin_email.lower(), json.dumps(admin_doc))
            )
            self.conn.commit()

    def __getitem__(self, item: str):
        if item == "users":
            return self.users
        elif item == "files":
            return self.files
        elif item == "records":
            return self.records
        return SQLiteCollection(self.conn, item)


# Database initialization with transparent fallback
_db_instance = None
_client_instance = None
_is_mongodb = False


def _init_db():
    global _db_instance, _client_instance, _is_mongodb
    if _db_instance is not None:
        return

    # 1. Try connecting to MongoDB (Atlas cần timeout cao hơn localhost)
    is_atlas = "mongodb+srv" in MONGODB_URL or "mongodb.net" in MONGODB_URL
    timeout_ms = 8000 if is_atlas else 1500
    try:
        test_client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=timeout_ms)
        test_client.admin.command('ping')
        test_client.close()
        _client_instance = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=timeout_ms)
        _db_instance = _client_instance[DATABASE_NAME]
        _is_mongodb = True
        print(f"✅ [Database] Kết nối MongoDB thành công: {'Atlas Cloud' if is_atlas else MONGODB_URL}")
    except Exception as e:
        # 2. Fallback to SQLite
        _is_mongodb = False
        _client_instance = None
        _db_instance = SQLiteDatabase(SQLITE_DB_PATH)
        print(f"⚠️  [Database] MongoDB không khả dụng ({type(e).__name__}). Đang dùng SQLite cục bộ.")


_init_db()


def get_database():
    return _db_instance


def is_mongodb():
    return _is_mongodb


def get_db_path():
    return SQLITE_DB_PATH


# Re-export client and db for backwards compatibility
client = _client_instance
db = _db_instance
