from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from app.core.redis import get_cache, set_cache, delete_cache
from app.db.session import get_db
from app.api.deps import require_project_member
from app.models.task import Task
from app.models.project_member import ProjectMember
from app.schemas.task import TaskCreate, TaskRead

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
