from collections import defaultdict

from sqlalchemy.orm import Session, joinedload

from src.db.tables import Answer, Question, QuestionCategoryEnum
from src.schema.answer import AnswerCreate
from src.schema.composite_schema import AnsweredQARead, UserAnswerGroupRead


def get_user_qna(db: Session, user_id: str) -> list[UserAnswerGroupRead]:
    user_answers = (
        db.query(Answer)
        .options(joinedload(Answer.question))
        .filter(Answer.user_id == user_id)
        .all()
    )

    grouped_answers = defaultdict(list)
    for answer in user_answers:
        if answer.question:
            grouped_answers[answer.question.category].append(
                AnsweredQARead(
                    answer_text=answer.answer_text,
                    question=answer.question,
                )
            )

    user_answer_groups = []
    for category, answers in grouped_answers.items():
        # TODO: フロントエンドのテンプレートIDとバックエンドのカテゴリの紐付け
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


def get_category_title(category: QuestionCategoryEnum) -> str:
    # 本来はDBや設定ファイルで管理するのが望ましい
    title_map = {
        QuestionCategoryEnum.self_introduction: "自己紹介のための20の質問",
        QuestionCategoryEnum.values: "価値観を知る30の質問",
        QuestionCategoryEnum.otaku: "オタクを語る50の質問",
        QuestionCategoryEnum.misc: "その他",
    }
    return title_map.get(category, "Q&A")


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
