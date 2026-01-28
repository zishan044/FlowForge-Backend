from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.api.deps import get_current_user, require_project_member
from app.models.task import Task
from app.models.user import User
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.schemas.task import TaskCreate, TaskRead

router = APIRouter(prefix='/tasks', tags=['tasks'])

@router.post('/', response_model=TaskRead)
async def create_task(
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    _: ProjectMember = Depends(require_project_member)
):
    task = Task(
        title=data.title,
        description=data.description,
        status=data.status,
        project_id=data.project_id,
        assignee_id=data.assignee_id
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

@router.get('/', response_model=list[TaskRead])
async def get_tasks(
    db: AsyncSession = Depends(get_db),
    member: ProjectMember = Depends(require_project_member),
):
    result = await db.execute(
        select(Task)
        .where(Task.project_id == member.project_id)
        .order_by(Task.created_at.desc())
    )
    return result.scalars().all()
