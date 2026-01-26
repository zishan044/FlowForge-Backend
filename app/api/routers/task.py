from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskRead

router = APIRouter(prefix='/tasks', tags=['tasks'])

@router.post('/', response_model=TaskRead)
async def create_task(
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
):
    task = Task(
        title=data.title,
        description=data.description,
        status=data.status or 'todo',
        project_id=data.project_id,
        assignee_id=data.assignee_id
    )


    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

@router.get('/', response_model=list[TaskRead])
async def get_tasks(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task))
    return result.scalars().all()