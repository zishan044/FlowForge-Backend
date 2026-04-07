from uuid import uuid4

from app.models.pasword_reset_token import PasswordResetToken
from app.schemas.password_reset_tokens import PasswordResetConfirm, PasswordResetRequest
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.schemas.token import Token, TokenData
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix='/auth', tags=['auth'])

@router.post("/signup", response_model=UserRead)
async def signup(
    data: UserCreate,
    db: AsyncSession = Depends(get_db)
):

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password)
    )

    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    return user

@router.post("/login", response_model=Token)
async def login(
    data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == data.email))
    db_user = result.scalar_one_or_none()

    if not db_user or not verify_password(data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token({
        "user_id": str(db_user.id),
        "email": db_user.email
    })

    return {
        'access_token': token,
        'token_type': 'bearer'
    }

@router.post("/password-reset/request")
async def password_reset_request(data: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user:
        return {"detail": "If an account with that email exists, a reset link has been sent"}

    token_str = str(uuid4())
    token = PasswordResetToken(user_id=user.id, token=token_str)
    db.add(token)
    await db.commit()

    # TODO: send email with link like: /auth/password-reset/confirm?token={token_str}
    print(f"Password reset token for {user.email}: {token_str}")

    return {"detail": "If an account with that email exists, a reset link has been sent"}

@router.post("/password-reset/confirm")
async def password_reset_confirm(data: PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PasswordResetToken).where(PasswordResetToken.token == data.token))
    token = result.scalar_one_or_none()
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    user = token.user
    user.hashed_password = hash_password(data.new_password)
    await db.delete(token)
    await db.commit()

    return {"detail": "Password has been reset successfully"}