from http.client import HTTPException

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from app.core.redis import get_cache, set_cache, delete_cache
from app.db.session import get_db
from app.api.deps import require_project_member, require_project_admin
from app.models.task import Task
from app.models.project_member import ProjectMember
from app.schemas.task import TaskCreate, TaskUpdate, TaskRead

router = APIRouter(prefix='/tasks', tags=['tasks'])

@router.post('/{project_id}', response_model=TaskRead)
async def create_task(
    project_id: int,
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    _: ProjectMember = Depends(require_project_member)
):
    task = Task(
        title=data.title,
        description=data.description,
        status=data.status,
        project_id=project_id,
        assignee_id=data.assignee_id
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    await delete_cache(f"tasks:project:{project_id}")
    
    return task

@router.get('/{project_id}', response_model=list[TaskRead])
async def get_tasks(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    _: ProjectMember = Depends(require_project_member),
):
    cache_key = f"tasks:project:{project_id}"

    cached = await get_cache(cache_key)
    if cached:
        return json.loads(cached)
    
    result = await db.execute(
        select(Task)
        .where(Task.project_id == project_id)
        .order_by(Task.created_at.desc())
    )
    tasks = result.scalars().all()

    tasks_out = [TaskRead.model_validate(t) for t in tasks]

    await set_cache(
        cache_key,
        [t.model_dump() for t in tasks_out],
        ttl=60
    )

    return tasks_out

@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    _: ProjectMember = Depends(require_project_member)
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if data.title is not None:
        task.title = data.title
    if data.description is not None:
        task.description = data.description
    if data.status is not None:
        task.status = data.status
    if data.assignee_id is not None:
        task.assignee_id = data.assignee_id

    await db.commit()
    await db.refresh(task)
    await delete_cache(f"tasks:project:{task.project_id}")

    return task

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _: ProjectMember = Depends(require_project_member)
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    project_id = task.project_id

    await db.delete(task)
    await db.commit()

    await delete_cache(f"tasks:project:{project_id}")

    return {"detail": "Task deleted"}