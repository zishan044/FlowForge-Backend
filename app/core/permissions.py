from enum import Enum
from typing import Optional

from app.models.project_member import ProjectMember, ProjectRole


class PermissionLevel(int, Enum):
    MEMBER = 1
    ADMIN = 2
    OWNER = 3

ROLE_LEVEL_MAP = {
    ProjectRole.member: PermissionLevel.MEMBER,
    ProjectRole.admin: PermissionLevel.ADMIN,
    ProjectRole.owner: PermissionLevel.OWNER,
}

def get_permission_level(member: ProjectMember) -> PermissionLevel:
    return ROLE_LEVEL_MAP[member.role]


def has_min_permission(
    member: ProjectMember,
    required: PermissionLevel,
) -> bool:
    return get_permission_level(member) >= required


def is_project_member(member: Optional[ProjectMember]) -> bool:
    return member is not None


def is_project_admin(member: Optional[ProjectMember]) -> bool:
    if not member:
        return False
    return has_min_permission(member, PermissionLevel.ADMIN)


def is_project_owner(member: Optional[ProjectMember]) -> bool:
    if not member:
        return False
    return has_min_permission(member, PermissionLevel.OWNER)
