"""Integration tests (real DB, rolled back per test) for per-org reading
plan calendars and quiz banks: a Church/Fellowship admin can run their own
calendar/quiz bank, separate from the platform default and from every other
org, and a member explicitly chooses (in Settings) which one they follow -
falling back to the platform default for anything the org hasn't
customized."""
from datetime import date

import pytest
import sqlalchemy as sa

from app.core.exceptions import ForbiddenError
from app.services.community_service import CommunityService
from app.services.progress_service import ProgressService
from app.services.reading_plan_service import ReadingPlanService
from app.services.quiz_service import QuizService
from app.schemas.community import ChurchCreate, FellowshipCreate
from app.schemas.reading import ReadingPlanCreate
from app.schemas.quiz import QuizQuestionCreate


@pytest.fixture()
def genesis_1_chapter_id(db):
    code = db.execute(sa.text("select code from bible_version where is_active limit 1")).scalar()
    return QuizService(db).resolve_chapter_id(code, "Genesis", 1)


@pytest.fixture()
def platform_today(db):
    """A platform-default reading plan day dated today, so get_today_reading
    always has a baseline to fall back to. The dev DB already has a seeded
    platform calendar, so pick a day_number far outside its range to avoid
    colliding with it - today's date must still be unique, so free any
    existing seeded row for today first."""
    existing = db.execute(sa.text("select id from reading_plan where reading_date = :d and scope_key = 'platform'"), {"d": date.today()}).scalar()
    if existing:
        db.execute(sa.text("delete from reading_plan where id = :id"), {"id": existing})
    max_day = db.execute(sa.text("select coalesce(max(day_number), 0) from reading_plan where scope_key = 'platform'")).scalar()
    plan_service = ReadingPlanService(db)
    return plan_service.create(ReadingPlanCreate(day_number=max_day + 1000, reading_date=date.today(), old_testament="Genesis 1", new_testament="Matthew 1"))


def test_org_admin_can_run_own_calendar_isolated_from_platform(db, make_user, platform_today):
    owner = make_user()
    community = CommunityService(db)
    church = community.admin_create_church(owner.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email=owner.email))

    church_plans = ReadingPlanService(db, church_id=church.id)
    church_plans.create(ReadingPlanCreate(day_number=1, reading_date=platform_today.reading_date, old_testament="Genesis 2", new_testament="Matthew 2"))

    # the platform's own calendar (scope_key="platform") must be untouched -
    # the fixture's own day is still there with its original content, and
    # the church's new day never shows up in it.
    platform_plans = ReadingPlanService(db)
    platform_day = platform_plans.get(platform_today.id)
    assert platform_day.old_testament == "Genesis 1"
    church_day_ids = {p.id for p in church_plans.list()[0]}
    assert platform_today.id not in church_day_ids

    org_items, org_total = church_plans.list()
    assert org_total == 1
    assert org_items[0].old_testament == "Genesis 2"


def test_non_admin_member_cannot_manage_org_reading_plan(db, make_user, platform_today):
    owner = make_user()
    member = make_user()
    community = CommunityService(db)
    church = community.admin_create_church(owner.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email=owner.email))
    request = community.request_join_church(member.id, church_id=church.id)
    community.respond_to_church_request(owner.id, request.id, approve=True)

    with pytest.raises(ForbiddenError):
        community._require_admin("church", church.id, member.id)


def test_member_follows_platform_default_until_choosing_org_calendar(db, make_user, platform_today):
    owner = make_user()
    member = make_user()
    community = CommunityService(db)
    church = community.admin_create_church(owner.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email=owner.email))
    request = community.request_join_church(member.id, church_id=church.id)
    community.respond_to_church_request(owner.id, request.id, approve=True)

    ReadingPlanService(db, church_id=church.id).create(
        ReadingPlanCreate(day_number=1, reading_date=platform_today.reading_date, old_testament="Genesis 2")
    )

    progress = ProgressService(db)
    # before choosing, still platform content
    assert progress.get_today_reading(member.id).old_testament == "Genesis 1"

    community.set_active_calendar(member.id, "church", church.id)
    assert progress.get_today_reading(member.id).old_testament == "Genesis 2"


def test_falls_back_to_platform_for_a_day_the_org_has_not_customized(db, make_user, platform_today):
    owner = make_user()
    member = make_user()
    community = CommunityService(db)
    church = community.admin_create_church(owner.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email=owner.email))
    request = community.request_join_church(member.id, church_id=church.id)
    community.respond_to_church_request(owner.id, request.id, approve=True)
    community.set_active_calendar(member.id, "church", church.id)

    # church has NOT created a reading_plan row for today - must fall back
    progress = ProgressService(db)
    today_reading = progress.get_today_reading(member.id)
    assert today_reading.old_testament == "Genesis 1"
    assert today_reading.day_number == platform_today.day_number
    assert today_reading.id == platform_today.id


def test_cannot_set_active_calendar_to_an_org_not_a_member_of(db, make_user):
    owner = make_user()
    outsider = make_user()
    community = CommunityService(db)
    church = community.admin_create_church(owner.id, ChurchCreate(name="Grace Chapel", privacy="public"))

    with pytest.raises(ForbiddenError):
        community.set_active_calendar(outsider.id, "church", church.id)


def test_calendar_options_only_lists_orgs_that_have_started_their_own_calendar(db, make_user):
    super_admin = make_user(role="super_admin")
    member = make_user()
    community = CommunityService(db)
    church_with_calendar = community.admin_create_church(super_admin.id, ChurchCreate(name="Has Calendar", privacy="public"))
    church_without_calendar = community.admin_create_church(super_admin.id, ChurchCreate(name="No Calendar Yet", privacy="public"))

    for church in (church_with_calendar, church_without_calendar):
        request = community.request_join_church(member.id, church_id=church.id)
        # super_admin has platform-wide override to approve on any org's behalf
        community.respond_to_church_request(super_admin.id, request.id, approve=True)

    ReadingPlanService(db, church_id=church_with_calendar.id).create(
        ReadingPlanCreate(day_number=1, reading_date=date.today(), old_testament="Genesis 3")
    )

    options = community.list_calendar_options(member.id)
    names = {o["name"] for o in options}
    assert "Has Calendar" in names
    assert "No Calendar Yet" not in names


def test_org_quiz_bank_isolated_from_platform_and_falls_back_when_empty(db, make_user, genesis_1_chapter_id):
    owner = make_user()
    member = make_user()
    community = CommunityService(db)
    church = community.admin_create_church(owner.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email=owner.email))
    request = community.request_join_church(member.id, church_id=church.id)
    community.respond_to_church_request(owner.id, request.id, approve=True)

    # platform bank has a question
    platform_quiz = QuizService(db)
    platform_quiz.admin_create_question(owner.id, genesis_1_chapter_id, QuizQuestionCreate(
        question="Platform question?", options=["A", "B"], correct_index=0, verse_reference="Genesis 1:1",
    ))

    # before the member has an active org calendar, they see the platform bank
    assert len(QuizService(db).get_quiz_for_chapter(genesis_1_chapter_id, user_id=member.id).questions) == 1

    community.set_active_calendar(member.id, "church", church.id)
    # church has no questions of its own yet -> falls back to platform bank
    assert len(QuizService(db).get_quiz_for_chapter(genesis_1_chapter_id, user_id=member.id).questions) == 1

    # church admin adds its own question - now isolated from the platform bank
    church_quiz = QuizService(db, church_id=church.id)
    church_quiz.admin_create_question(owner.id, genesis_1_chapter_id, QuizQuestionCreate(
        question="Church-only question?", options=["X", "Y"], correct_index=1, verse_reference="Genesis 1:2",
    ))

    member_questions = QuizService(db).get_quiz_for_chapter(genesis_1_chapter_id, user_id=member.id).questions
    assert len(member_questions) == 1
    assert member_questions[0].question == "Church-only question?"

    # the platform bank (and any other org) never sees the church's own question
    assert len(platform_quiz.admin_list_questions_for_chapter(genesis_1_chapter_id)) == 1
    assert len(church_quiz.admin_list_questions_for_chapter(genesis_1_chapter_id)) == 1


def test_org_admin_cannot_edit_platform_or_other_orgs_quiz_question(db, make_user, genesis_1_chapter_id):
    owner_a = make_user()
    owner_b = make_user()
    community = CommunityService(db)
    church_a = community.admin_create_church(owner_a.id, ChurchCreate(name="Church A", privacy="public"))
    church_b = community.admin_create_church(owner_b.id, ChurchCreate(name="Church B", privacy="public"))

    quiz_a = QuizService(db, church_id=church_a.id)
    question = quiz_a.admin_create_question(owner_a.id, genesis_1_chapter_id, QuizQuestionCreate(
        question="Church A question?", options=["A", "B"], correct_index=0, verse_reference="Genesis 1:1",
    ))

    quiz_b = QuizService(db, church_id=church_b.id)
    from app.core.exceptions import NotFoundError
    with pytest.raises(NotFoundError):
        quiz_b.admin_delete_question(owner_b.id, question.id)

    platform_quiz = QuizService(db)
    with pytest.raises(NotFoundError):
        platform_quiz.admin_delete_question(owner_a.id, question.id)
