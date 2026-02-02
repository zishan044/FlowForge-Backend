
from app.core.config import settings

async def send_invite_email(
    to_email: str,
    project_name: str,
    invited_by: str
):
    # In real life: SMTP / SES / SendGrid
    print(
        f"[EMAIL] To: {to_email} | "
        f"Project: {project_name} | "
        f"Invited by: {invited_by}"
    )
