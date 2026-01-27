from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.models.project_member import ProjectMember
from app.core.security import decode_access_token
from app.core.permissions import is_project_member, is_project_admin, is_project_owner

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    try:
        payload = decode_access_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user

async def get_project_member(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectMember | None:
    query = select(ProjectMember).where(ProjectMember.user_id == current_user.id, ProjectMember.project_id == project_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def require_project_member(
    project_id: int,
    member: ProjectMember = Depends(get_project_member),
) -> ProjectMember:
    if not is_project_member(member):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not a project member'
        )
    return member


async def require_project_admin(
    project_id: int,
    member: ProjectMember = Depends(require_project_member),
) -> ProjectMember:
    if not is_project_admin(member):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Admin permission required'
        )
    return member


async def require_project_owner(
    project_id: int,
    member: ProjectMember = Depends(require_project_member)
) -> ProjectMember:
    if not is_project_owner(member):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Owner permission required'
        )
    return member