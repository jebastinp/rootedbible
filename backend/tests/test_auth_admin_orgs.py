"""Integration tests (real DB, rolled back per test) for the admin_orgs
field on the sign-in response: lets the frontend route a Church/Fellowship
owner/admin straight to their org's own admin page, without touching their
platform-wide role."""
from app.services.auth_service import AuthService
from app.services.community_service import CommunityService
from app.schemas.community import ChurchCreate, FellowshipCreate


def test_plain_member_has_no_admin_orgs(db, make_user):
    user = make_user()
    response = AuthService(db).login(user.user_id)
    assert response.admin_orgs == []


def test_church_owner_sees_their_church_in_admin_orgs(db, make_user):
    owner = make_user()
    community = CommunityService(db)
    church = community.admin_create_church(owner.id, ChurchCreate(name="Grace Chapel", privacy="public"))

    response = AuthService(db).login(owner.user_id)

    assert len(response.admin_orgs) == 1
    assert response.admin_orgs[0].kind == "church"
    assert response.admin_orgs[0].org_id == church.id
    assert response.admin_orgs[0].name == "Grace Chapel"
    # running a church must never grant a platform-wide role
    assert response.user.role.value == "member"


def test_plain_church_member_not_admin_has_no_admin_orgs(db, make_user):
    owner = make_user()
    member = make_user()
    community = CommunityService(db)
    church = community.admin_create_church(owner.id, ChurchCreate(name="Grace Chapel", privacy="public"))
    request = community.request_join_church(member.id, church_id=church.id)
    community.respond_to_church_request(owner.id, request.id, approve=True)

    response = AuthService(db).login(member.user_id)
    assert response.admin_orgs == []


def test_fellowship_admin_sees_their_fellowship_in_admin_orgs(db, make_user):
    owner = make_user()
    community = CommunityService(db)
    fellowship = community.admin_create_fellowship(owner.id, FellowshipCreate(name="Youth Fellowship", privacy="public"))

    response = AuthService(db).login(owner.user_id)

    assert len(response.admin_orgs) == 1
    assert response.admin_orgs[0].kind == "fellowship"
    assert response.admin_orgs[0].org_id == fellowship.id
