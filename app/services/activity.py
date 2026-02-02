from app.core.logging import get_logger

logger = get_logger("activity")

async def log_activity(
    event: str,
    user_id: int,
    project_id: int | None = None,
    metadata: dict | None = None
):
    logger.info(
        "activity_event",
        extra={
            "event": event,
            "user_id": user_id,
            "project_id": project_id,
            "metadata": metadata,
        }
    )
