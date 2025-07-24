from collections import defaultdict

from sqlalchemy.orm import Session, joinedload

from src.db.tables import Answer, Question, QuestionCategoryEnum
from src.schema.answer import AnswerCreate
from src.schema.composite_schema import AnsweredQARead, UserAnswerGroupRead
from src.service.question_templates import get_category_title, get_default_templates


def get_user_qna(db: Session, user_id: str) -> list[UserAnswerGroupRead]:
    # ユーザーの回答を取得
    user_answers = (
        db.query(Answer)
        .options(joinedload(Answer.question))
        .filter(Answer.user_id == user_id)
        .all()
    )

    # 回答をquestion_idでマッピング
    answers_by_question_id = {answer.question_id: answer for answer in user_answers}

    # 回答済みの質問のカテゴリを取得
    answered_categories = set()
    for answer in user_answers:
        if answer.question:
            answered_categories.add(answer.question.category)

    # カテゴリ内のすべての質問を取得し、回答状況と合わせて返す
    user_answer_groups = []
    for category in answered_categories:
        # このカテゴリのすべての質問を取得
        category_questions = (
            db.query(Question)
            .filter(Question.category == category)
            .order_by(Question.display_order)
            .all()
        )

        # 各質問に対して回答があるかチェック
        answers = []
        for question in category_questions:
            user_answer = answers_by_question_id.get(question.question_id)
            answers.append(
                AnsweredQARead(
                    answer_text=user_answer.answer_text if user_answer else "",
                    question=question,
                )
            )

        user_answer_groups.append(
            UserAnswerGroupRead(
                template_id=category.name,
                template_title=get_category_title(category),
                answers=answers,
            )
        )

    return user_answer_groups


def get_all_questions_grouped(
    db: Session,
) -> dict[QuestionCategoryEnum, list[Question]]:
    questions = db.query(Question).order_by(Question.display_order).all()
    grouped_questions = defaultdict(list)
    for q in questions:
        grouped_questions[q.category].append(q)
    return grouped_questions


# Remove this function as it's now imported from question_templates


def get_all_questions(db: Session) -> list[Question]:
    return db.query(Question).order_by(Question.display_order).all()


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
    """Initialize default questions in the database if they don't exist."""
    # Check if questions already exist
    existing_questions = db.query(Question).first()
    if existing_questions:
        return

    # Get default templates and create questions
    templates = get_default_templates()

    for template in templates:
        for i, question_text in enumerate(template.questions, 1):
            question = Question(
                category=template.category, text=question_text, display_order=i
            )
            db.add(question)

    db.commit()
