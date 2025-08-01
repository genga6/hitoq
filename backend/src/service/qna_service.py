from collections import defaultdict

from sqlalchemy.orm import Session, joinedload

from src.db.tables import Answer, Question
from src.schema.answer import AnswerCreate
from src.schema.composite_schema import AnsweredQARead, UserAnswerGroupRead
from src.schema.question import QuestionRead
from src.service.categories import get_category_by_id
from src.service.yaml_loader import get_yaml_loader


def get_user_qna(db: Session, user_id: str) -> list[UserAnswerGroupRead]:
    user_answers = (
        db.query(Answer)
        .options(joinedload(Answer.question))
        .filter(Answer.user_id == user_id)
        .all()
    )

    answers_by_question_id = {answer.question_id: answer for answer in user_answers}

    answered_categories = set()
    for answer in user_answers:
        if answer.question:
            answered_categories.add(answer.question.category_id)

    user_answer_groups = []
    for category_id in answered_categories:
        category_info = get_category_by_id(category_id)
        if not category_info:
            continue

        category_questions = (
            db.query(Question)
            .filter(Question.category_id == category_id)
            .order_by(Question.display_order)
            .all()
        )

        answers = []
        for question in category_questions:
            user_answer = answers_by_question_id.get(question.question_id)
            answers.append(
                AnsweredQARead(
                    answer_text=user_answer.answer_text if user_answer else "",
                    question=QuestionRead.model_validate(question),
                )
            )

        user_answer_groups.append(
            UserAnswerGroupRead(
                template_id=category_id,
                template_title=category_info.name,
                answers=answers,
            )
        )

    return user_answer_groups


def get_all_questions_grouped(
    db: Session,
) -> dict[str, list[Question]]:
    questions = db.query(Question).order_by(Question.display_order).all()
    grouped_questions = defaultdict(list)
    for q in questions:
        grouped_questions[q.category_id].append(q)
    return grouped_questions


def get_all_questions(db: Session) -> list[Question]:
    return db.query(Question).order_by(Question.display_order).all()


def get_questions_by_category(db: Session, category_id: str) -> list[Question]:
    """指定されたカテゴリの質問を取得（ガチャ機能用）"""
    return (
        db.query(Question)
        .filter(Question.category_id == category_id)
        .order_by(Question.display_order)
        .all()
    )


def create_answer(
    db: Session, user_id: str, question_id: int, answer_in: AnswerCreate
) -> Answer:
    db_answer = Answer(
        user_id=user_id, question_id=question_id, **answer_in.model_dump()
    )
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return db_answer


def initialize_default_questions(db: Session) -> None:
    existing_questions = db.query(Question).first()
    if existing_questions:
        return

    loader = get_yaml_loader()
    templates = loader.load_templates()

    for template in templates:
        for i, question_text in enumerate(template.questions, 1):
            question = Question(
                category_id=template.category_id, text=question_text, display_order=i
            )
            db.add(question)

    db.commit()
