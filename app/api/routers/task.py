from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.task import Task
from app.models.user import User
from app.models.project import Project
from app.schemas.task import TaskCreate, TaskRead

router = APIRouter(prefix='/tasks', tags=['tasks'])

@router.post('/', response_model=TaskRead)
async def create_task(
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Project).where(Project.id == data.project_id, Project.owner_id == current_user.id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Project not found or not owned by user"
        )

    task = Task(
        title=data.title,
        description=data.description,
        status=data.status or 'todo',
        project_id=data.project_id,
        assignee_id=current_user.id
    )


    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

@router.get('/', response_model=list[TaskRead])
async def get_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Task)
        .where(Task.assignee_id == current_user.id)
        .order_by(Task.created_at.desc())
    )
    return result.scalars().all()