import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from database import get_database
from auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])

class RegisterSchema(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
async def register(payload: RegisterSchema):
    db = get_database()
    existing = await db.users.find_one({"email": payload.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã tồn tại trên hệ thống."
        )

    user_id = str(uuid.uuid4())
    new_user = {
        "_id": user_id,
        "email": payload.email,
        "full_name": payload.full_name,
        "hashed_password": hash_password(payload.password),
        "role": "user",
        "is_approved": False  # Admin approval required
    }
    await db.users.insert_one(new_user)
    return {
        "message": "Đăng ký thành công! Vui lòng chờ Admin phê duyệt tài khoản.",
        "user_id": user_id
    }

@router.post("/login")
async def login(payload: LoginSchema):
    db = get_database()
    user = await db.users.find_one({"email": payload.email})
    if not user or not verify_password(payload.password, user.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác."
        )

    if not user.get("is_approved", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản của bạn chưa được Admin phê duyệt."
        )

    token = create_access_token({"sub": user["_id"], "email": user["email"], "role": user.get("role", "user")})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["_id"],
            "email": user["email"],
            "full_name": user.get("full_name", ""),
            "role": user.get("role", "user")
        }
    }

@router.get("/me")
async def me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["_id"],
        "email": current_user["email"],
        "full_name": current_user.get("full_name", ""),
        "role": current_user.get("role", "user"),
        "is_approved": current_user.get("is_approved", True)
    }
