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

@router.post("/signup/", response_model=UserRead)
async def signup(
    data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    
    print("password:", data.password)
    print("len(password):", len(data.password))
    print("len(bytes):", len(data.password.encode("utf-8")))

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

@router.post("/login/", response_model=Token)
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
        "sub": str(db_user.id),
        "email": db_user.email
    })

    return {
        'access_token': token,
        'token_type': 'bearer'
    }
