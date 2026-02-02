from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import Depends, APIRouter, HTTPException, status
import json

from app.schemas.project_invite import ProjectInviteCreate, ProjectInviteRead, ProjectInviteUpdate
from app.core.redis import get_cache, set_cache, delete_cache
from app.db.session import get_db
from app.models.user import User
from app.models.project_invite import ProjectInvite
from app.models.project_member import ProjectMember
from app.api.deps import get_current_user, require_project_admin

router = APIRouter(prefix='/projects', tags=['project_invites'])

@router.post('/{project_id}/invites', response_model=ProjectInviteRead)
async def send_invite(
    project_id: int,
    data: ProjectInviteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_project_admin)
):
    existing = await db.execute(
        select(ProjectInvite).where(
            ProjectInvite.project_id == project_id,
            ProjectInvite.invited_user_id == data.invited_user_id,
            ProjectInvite.status == 'pending'
        )
    )

    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User already invited'
        )
    
    if data.invited_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='You cannot invite yourself'
        )
    
    invite = ProjectInvite(
        project_id=project_id,
        invited_user_id=data.invited_user_id,
        invited_by_id=current_user.id,
    )

    db.add(invite)
    await db.commit()

    query = (
        select(ProjectInvite)
        .options(
            selectinload(ProjectInvite.invited_user),
            selectinload(ProjectInvite.invited_by)
        )
        .where(ProjectInvite.id == invite.id)
    )
    result = await db.execute(query)
    invite = result.scalar_one()

    await delete_cache(f"invites:user:{data.invited_user_id}")

    return invite

@router.get('/{project_id}/invites', response_model=list[ProjectInviteRead])
async def get_invites_by_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_project_admin)
):
    query = (
        select(ProjectInvite)
        .options(
            selectinload(ProjectInvite.invited_user),
            selectinload(ProjectInvite.invited_by)
        )
        .where(ProjectInvite.project_id == project_id)
    )
    result = await db.execute(query)
    invites = result.scalars().all()

    return invites


@router.get('/invites', response_model=list[ProjectInviteRead])
async def get_invites_by_user(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    cache_key = f"invites:user:{current_user.id}"
    cached = await get_cache(cache_key)
    if cached:
        return json.loads(cached)
    
    query = (
        select(ProjectInvite)
        .options(
            selectinload(ProjectInvite.invited_user),
            selectinload(ProjectInvite.invited_by)
        )
        .where(ProjectInvite.invited_user_id == current_user.id)
    )
    result = await db.execute(query)
    invites = result.scalars().all()

    invites_out = [ProjectInviteRead.model_validate(i) for i in invites]
    await set_cache(cache_key, [i.model_dump() for i in invites_out])
    
    return invites_out

@router.patch('/invites/{invite_id}', response_model=ProjectInviteRead)
async def update_invite(
    invite_id: int,
    data: ProjectInviteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(ProjectInvite)
        .options(
            selectinload(ProjectInvite.invited_user),
            selectinload(ProjectInvite.invited_by)
        )
        .where(ProjectInvite.id == invite_id)
    )
    result = await db.execute(query)
    invite = result.scalar_one_or_none()

    if not invite or invite.status != 'pending' or current_user.id != invite.invited_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid invite'
        )
    
    if data.status == 'accepted':
        member = ProjectMember(
            project_id=invite.project_id,
            user_id=current_user.id,
            role='member'
        )
        db.add(member)

    invite.status = data.status
    await db.commit()

    query = (
        select(ProjectInvite)
        .options(
            selectinload(ProjectInvite.invited_user),
            selectinload(ProjectInvite.invited_by)
        )
        .where(ProjectInvite.id == invite.id)
    )
    result = await db.execute(query)
    invite = result.scalar_one()

    await delete_cache(f"invites:user:{current_user.id}")

    return invite