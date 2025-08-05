from sqlalchemy.orm import Session

from src.db.session import SessionLocal
from src.db.tables import Question
from src.service.question_templates import get_default_templates


def seed_questions():
    """Seed the database with default question templates."""
    db: Session = SessionLocal()
    try:
        # Clear existing questions to avoid duplicates
        print("Clearing existing questions...")
        db.query(Question).delete()
        db.commit()

        templates = get_default_templates()
        total_questions = 0

        for template in templates:
            # テンプレートごとに一意のIDを生成（テンプレートタイトルから）
            template_id = (
                template.title.replace(" ", "-")
                .replace("の", "")
                .replace("質問", "")
                .lower()
            )
            print(
                f"Adding template: {template.title} (ID: {template_id}, {len(template.questions)} questions)"
            )

            for i, question_text in enumerate(template.questions, 1):
                question = Question(
                    category=template.category,
                    text=question_text,
                    display_order=i,
                    template_id=template_id,
                )
                db.add(question)
                total_questions += 1

        db.commit()
        print(
            f"Successfully seeded {total_questions} questions from {len(templates)} templates."
        )

        # Verify the seeding by template
        for template in templates:
            template_id = (
                template.title.replace(" ", "-")
                .replace("の", "")
                .replace("質問", "")
                .lower()
            )
            count = (
                db.query(Question).filter(Question.template_id == template_id).count()
            )
            print(f"  {template.title} ({template_id}): {count} questions")

    except Exception as e:
        print(f"Error seeding questions: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_questions()
