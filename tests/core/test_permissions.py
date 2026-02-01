import pytest
from app.core.permissions import (
    PermissionLevel, 
    has_min_permission, 
    is_project_admin, 
    is_project_owner, 
    is_project_member
)
from app.models.project_member import ProjectMember, ProjectRole

@pytest.fixture
def member_user():
    return ProjectMember(role=ProjectRole.member)

@pytest.fixture
def admin_user():
    return ProjectMember(role=ProjectRole.admin)

@pytest.fixture
def owner_user():
    return ProjectMember(role=ProjectRole.owner)


def test_permission_hierarchy(member_user, admin_user, owner_user):

    assert has_min_permission(owner_user, PermissionLevel.OWNER) is True
    assert has_min_permission(owner_user, PermissionLevel.ADMIN) is True
    assert has_min_permission(owner_user, PermissionLevel.MEMBER) is True

    assert has_min_permission(member_user, PermissionLevel.ADMIN) is False
    assert has_min_permission(member_user, PermissionLevel.OWNER) is False


def test_is_project_member():
    assert is_project_member(ProjectMember(role=ProjectRole.member)) is True
    assert is_project_member(None) is False

def test_is_project_admin(admin_user, member_user):
    assert is_project_admin(admin_user) is True
    assert is_project_admin(member_user) is False
    assert is_project_admin(None) is False

def test_is_project_owner(owner_user, admin_user):
    assert is_project_owner(owner_user) is True
    assert is_project_owner(admin_user) is False
    assert is_project_owner(None) is False


def test_role_level_mapping_integrity():
    
    assert PermissionLevel.OWNER > PermissionLevel.ADMIN
    assert PermissionLevel.ADMIN > PermissionLevel.MEMBER