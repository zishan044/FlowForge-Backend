from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.api.deps import get_current_user, require_project_admin, require_project_owner, require_project_member
from app.models.project import Project
from app.models.user import User
from app.schemas.user import UserRead
from app.models.project_member import ProjectMember, ProjectRole
from app.schemas.project import ProjectCreate, ProjectRead
from app.schemas.project_member import ProjectMemberCreate, ProjectMemberRead

router = APIRouter(prefix='/projects', tags=['projects'])

@router.post('/', response_model=ProjectRead)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = Project(
        name=data.name,
        owner_id=current_user.id
    )

    db.add(project)
    await db.commit()
    await db.refresh(project)

    owner_member = ProjectMember(
        project_id=project.id,
        user_id=current_user.id,
        role=ProjectRole.owner
    )

    db.add(owner_member)
    await db.commit()
    await db.refresh(owner_member)

    query = (
        select(Project)
        .options(
            selectinload(Project.members),
            selectinload(Project.tasks),
            selectinload(Project.invites)
        )
        .where(Project.id == project.id)
    )
    result = await db.execute(query)
    project = result.scalar_one()

    return project

@router.get('/', response_model=list[ProjectRead])
async def get_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Project).options(
        selectinload(Project.members),
        selectinload(Project.tasks),
        selectinload(Project.invites)
    ).join(ProjectMember, ProjectMember.project_id == Project.id).where(ProjectMember.user_id == current_user.id)
    result = await db.execute(query)
    projects = result.scalars().all()
    return projects

@router.post('/{project_id}/members', response_model=ProjectMemberRead)
async def add_member(
    project_id: int,
    data: ProjectMemberCreate,
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_project_admin)
):
    query = select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == data.user_id)
    result = await db.execute(query)
    db_member = result.scalar_one_or_none()

    if db_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Already a member'
        )

    member = ProjectMember(
        project_id = project_id,
        user_id = data.user_id,
        role = data.role
    )

    result = await db.execute(
        select(ProjectMember)
        .options(selectinload(ProjectMember.user))
        .where(ProjectMember.user_id == data.user_id, ProjectMember.project_id == project_id)
    )
    member = result.scalar_one()
    return member

@router.delete('/{project_id}/members/{user_id}')
async def delete_member(
    project_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_project_admin)
):
    query = select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
    result = await db.execute(query)
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Not a member'
        )
    
    if member.role == ProjectRole.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Cannot remove project owner'
        )
    
    await db.delete(member)
    await db.commit()
    return { 'detail': 'member removed' }

@router.get('/{project_id}/members', response_model=list[ProjectMemberRead])
async def get_members(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_project_member)
):
    query = select(ProjectMember).where(ProjectMember.project_id == project_id).join(User, User.id == ProjectMember.user_id)
    result = await db.execute(query)
    members = result.scalars().all()

    return [
        ProjectMemberRead.model_validate({
            "user_id": m.user_id,
            "user_info": m.user,
            "role": m.role
        })
        for m in members
    ]