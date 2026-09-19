from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from database import get_database
from auth import require_admin, hash_password

router = APIRouter(prefix="/api/admin", tags=["Admin"])

class UserApprovalSchema(BaseModel):
    user_id: str
    is_approved: bool

class ResetPasswordSchema(BaseModel):
    user_id: str
    new_password: str

@router.get("/users")
async def list_users(admin: dict = Depends(require_admin)):
    db = get_database()
    cursor = db.users.find({}, {"hashed_password": 0})
    users = await cursor.to_list(length=1000)
    return users

@router.post("/approve-user")
async def approve_user(payload: UserApprovalSchema, admin: dict = Depends(require_admin)):
    db = get_database()
    res = await db.users.update_one(
        {"_id": payload.user_id},
        {"$set": {"is_approved": payload.is_approved}}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    return {"message": f"Cập nhật trạng thái duyệt tài khoản thành công ({payload.is_approved})."}

@router.post("/reset-password")
async def reset_user_password(payload: ResetPasswordSchema, admin: dict = Depends(require_admin)):
    db = get_database()
    new_hash = hash_password(payload.new_password)
    res = await db.users.update_one(
        {"_id": payload.user_id},
        {"$set": {"hashed_password": new_hash}}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    return {"message": "Đã đổi mật khẩu người dùng thành công."}

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, admin: dict = Depends(require_admin)):
    db = get_database()
    res = await db.users.delete_one({"_id": user_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    return {"message": "Đã xóa tài khoản người dùng thành công."}
