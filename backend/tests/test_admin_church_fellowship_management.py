"""Integration tests (real DB, rolled back per test) for Super Admin's
edit/deactivate/reactivate/delete controls over any Church or Fellowship,
and for pending_admin_email being visible to admins (and hidden from
regular members)."""
import pytest

from app.core.exceptions import NotFoundError
from app.services.community_service import CommunityService
from app.schemas.community import ChurchCreate, FellowshipCreate, ChurchUpdate, FellowshipUpdate


def test_super_admin_can_edit_a_church(db, make_user):
    creator = make_user()
    super_admin = make_user(role="super_admin")
    community = CommunityService(db)
    church = community.admin_create_church(creator.id, ChurchCreate(name="Grace Chapel", privacy="public"))

    updated = community.admin_update_church(super_admin.id, church.id, ChurchUpdate(name="New Name", privacy="private"))

    assert updated.name == "New Name"
    assert updated.privacy == "private"


def test_super_admin_can_deactivate_and_reactivate_a_church(db, make_user):
    creator = make_user()
    super_admin = make_user(role="super_admin")
    community = CommunityService(db)
    church = community.admin_create_church(creator.id, ChurchCreate(name="Grace Chapel", privacy="public"))

    suspended = community.admin_set_church_status(super_admin.id, church.id, "suspended")
    assert suspended.status == "suspended"

    reactivated = community.admin_set_church_status(super_admin.id, church.id, "active")
    assert reactivated.status == "active"


def test_super_admin_can_delete_a_church(db, make_user):
    creator = make_user()
    super_admin = make_user(role="super_admin")
    community = CommunityService(db)
    church = community.admin_create_church(creator.id, ChurchCreate(name="Grace Chapel", privacy="public"))

    community.admin_delete_church(super_admin.id, church.id)

    with pytest.raises(NotFoundError):
        community._get_church(church.id)


def test_super_admin_can_edit_deactivate_delete_a_fellowship(db, make_user):
    creator = make_user()
    super_admin = make_user(role="super_admin")
    community = CommunityService(db)
    fellowship = community.admin_create_fellowship(creator.id, FellowshipCreate(name="Youth Fellowship", privacy="public"))

    updated = community.admin_update_fellowship(super_admin.id, fellowship.id, FellowshipUpdate(name="Renamed Fellowship"))
    assert updated.name == "Renamed Fellowship"

    suspended = community.admin_set_fellowship_status(super_admin.id, fellowship.id, "suspended")
    assert suspended.status == "suspended"

    community.admin_delete_fellowship(super_admin.id, fellowship.id)
    with pytest.raises(NotFoundError):
        community._get_fellowship(fellowship.id)


def test_pending_admin_email_visible_to_org_admin_and_super_admin_but_not_regular_member(db, make_user):
    owner = make_user()
    member = make_user()
    super_admin = make_user(role="super_admin")
    community = CommunityService(db)
    church = community.admin_create_church(owner.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email="future.admin@example.com"))
    request = community.request_join_church(member.id, church_id=church.id)
    community.respond_to_church_request(owner.id, request.id, approve=True)

    owner_view = community.get_church_detail(owner.id, church.id)
    assert owner_view.pending_admin_email == "future.admin@example.com"

    member_view = community.get_church_detail(member.id, church.id)
    assert member_view.pending_admin_email is None

    platform_list = community.admin_list_all_churches()
    listed = next(c for c in platform_list if c.id == church.id)
    assert listed.pending_admin_email == "future.admin@example.com"
