"""Integration tests (real DB, rolled back per test) for admin quiz
question management - CRUD plus the correct_index bounds check."""
import pytest

from app.core.exceptions import NotFoundError, ValidationError
from app.services.quiz_service import QuizService
from app.schemas.quiz import QuizQuestionCreate, QuizQuestionUpdate


@pytest.fixture()
def genesis_1_chapter_id(db):
    import sqlalchemy as sa
    code = db.execute(sa.text("select code from bible_version where is_active limit 1")).scalar()
    return QuizService(db).resolve_chapter_id(code, "Genesis", 1)


def test_create_list_update_delete_question(db, make_user, genesis_1_chapter_id):
    admin = make_user(role="admin")
    service = QuizService(db)

    created = service.admin_create_question(admin.id, genesis_1_chapter_id, QuizQuestionCreate(
        question="Who created the heavens and the earth?",
        options=["Moses", "God", "Abraham", "David"],
        correct_index=1,
        verse_reference="Genesis 1:1",
    ))
    assert created.correct_index == 1

    listed = service.admin_list_questions_for_chapter(genesis_1_chapter_id)
    assert len(listed) == 1
    assert listed[0].id == created.id

    updated = service.admin_update_question(admin.id, created.id, QuizQuestionUpdate(verse_reference="Genesis 1:1-3"))
    assert updated.verse_reference == "Genesis 1:1-3"

    service.admin_delete_question(admin.id, created.id)
    assert service.admin_list_questions_for_chapter(genesis_1_chapter_id) == []


def test_create_rejects_out_of_range_correct_index(db, make_user, genesis_1_chapter_id):
    admin = make_user(role="admin")
    service = QuizService(db)
    with pytest.raises(ValidationError):
        service.admin_create_question(admin.id, genesis_1_chapter_id, QuizQuestionCreate(
            question="Bad question", options=["A", "B"], correct_index=5, verse_reference="Genesis 1:1",
        ))


def test_update_rejects_out_of_range_correct_index(db, make_user, genesis_1_chapter_id):
    admin = make_user(role="admin")
    service = QuizService(db)
    created = service.admin_create_question(admin.id, genesis_1_chapter_id, QuizQuestionCreate(
        question="Question text", options=["A", "B", "C"], correct_index=0, verse_reference="Genesis 1:1",
    ))
    with pytest.raises(ValidationError):
        service.admin_update_question(admin.id, created.id, QuizQuestionUpdate(correct_index=10))


def test_update_rejects_narrowed_options_that_no_longer_fit_existing_correct_index(db, make_user, genesis_1_chapter_id):
    admin = make_user(role="admin")
    service = QuizService(db)
    created = service.admin_create_question(admin.id, genesis_1_chapter_id, QuizQuestionCreate(
        question="Question text", options=["A", "B", "C"], correct_index=2, verse_reference="Genesis 1:1",
    ))
    with pytest.raises(ValidationError):
        service.admin_update_question(admin.id, created.id, QuizQuestionUpdate(options=["A", "B"]))


def test_delete_nonexistent_question_raises_not_found(db, make_user):
    import uuid
    admin = make_user(role="admin")
    service = QuizService(db)
    with pytest.raises(NotFoundError):
        service.admin_delete_question(admin.id, uuid.uuid4())


def test_resolve_chapter_id_unknown_book_raises_not_found(db):
    import sqlalchemy as sa
    code = db.execute(sa.text("select code from bible_version where is_active limit 1")).scalar()
    service = QuizService(db)
    with pytest.raises(NotFoundError):
        service.resolve_chapter_id(code, "NotARealBook", 1)
