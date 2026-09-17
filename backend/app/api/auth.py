"""认证接口：注册 / 登录 / 当前用户"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserOut, TokenOut
from app.core.security import hash_password, verify_password, create_access_token
from app.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=TokenOut, summary="注册并登录")
def register(payload: UserRegister, db: Session = Depends(get_db)):
    exists = db.query(User).filter(
        (User.username == payload.username) | (User.email == payload.email)
    ).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名或邮箱已存在")
    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenOut, summary="登录")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    # 支持用户名或邮箱
    user = db.query(User).filter(
        (User.username == payload.identifier) | (User.email == payload.identifier)
    ).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名/邮箱或密码错误")
    token = create_access_token(user.id)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut, summary="获取当前用户")
def me(current: User = Depends(get_current_user)):
    return UserOut.model_validate(current)
