import asyncio
import uuid
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import get_database, is_mongodb, get_db_path, MONGODB_URL
from auth import hash_password

async def main():
    db = get_database()
    admin_email = os.getenv("ADMIN_EMAIL", "admin@transport.com")
    admin_pass = os.getenv("ADMIN_PASSWORD", "admin123456")

    print("=" * 60)
    if is_mongodb():
        print(f"📦 [Database] Đang kết nối tới MongoDB: {MONGODB_URL}")
    else:
        print(f"📦 [Database] Đang sử dụng lưu trữ cục bộ SQLite: {get_db_path()}")

    existing = await db.users.find_one({"email": admin_email})
    if existing:
        print(f"ℹ️ Tài khoản admin ({admin_email}) đã tồn tại trên hệ thống.")
        print(f"   Email:    {admin_email}")
        print(f"   Mật khẩu: {admin_pass}")
        print("=" * 60)
        return

    admin_doc = {
        "_id": str(uuid.uuid4()),
        "email": admin_email,
        "full_name": "System Administrator",
        "hashed_password": hash_password(admin_pass),
        "role": "admin",
        "is_approved": True,
        "created_at": datetime.now().isoformat()
    }

    await db.users.insert_one(admin_doc)
    print(f"✅ Đã tạo tài khoản admin thành công!")
    print(f"   Email:    {admin_email}")
    print(f"   Mật khẩu: {admin_pass}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
