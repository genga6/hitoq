from unittest.mock import Mock, patch

import pytest

from src.db.tables import Answer, Question
from src.schema.answer import AnswerCreate
from src.service import qna_service


@pytest.mark.unit
class TestQnaService:
    def test_get_user_qna_with_answers(
        self, test_db_session, create_user, create_question, create_answer
    ):
        user = create_user(user_id="test_user")
        question1 = create_question(
            category_id="personality", text="性格について教えて"
        )
        question2 = create_question(
            category_id="personality", text="趣味は何ですか", display_order=2
        )

        create_answer(user.user_id, question1.question_id, "明るい性格です")
        create_answer(user.user_id, question2.question_id, "読書が好きです")

        result = qna_service.get_user_qna(test_db_session, user.user_id)

        assert len(result) == 1  # 1つのカテゴリ
        assert result[0].template_id == "personality"
        assert result[0].template_title == "性格・特徴"
        assert len(result[0].answers) == 2

        # 回答の確認
        answers = {
            answer.question.text: answer.answer_text for answer in result[0].answers
        }
        assert answers["性格について教えて"] == "明るい性格です"
        assert answers["趣味は何ですか"] == "読書が好きです"

    def test_get_user_qna_no_answers(self, test_db_session, create_user):
        user = create_user(user_id="test_user")

        result = qna_service.get_user_qna(test_db_session, user.user_id)

        assert result == []

    def test_get_user_qna_mixed_categories(
        self, test_db_session, create_user, create_question, create_answer
    ):
        user = create_user(user_id="test_user")
        question1 = create_question(category_id="personality", text="性格について")
        question2 = create_question(
            category_id="lifestyle", text="ライフスタイルについて"
        )

        create_answer(user.user_id, question1.question_id, "回答1")
        create_answer(user.user_id, question2.question_id, "回答2")

        result = qna_service.get_user_qna(test_db_session, user.user_id)

        assert len(result) == 2
        category_ids = [group.template_id for group in result]
        assert "personality" in category_ids
        assert "lifestyle" in category_ids

    def test_get_all_questions_grouped(self, test_db_session, create_question):
        create_question(category_id="personality", text="質問1", display_order=1)
        create_question(category_id="personality", text="質問2", display_order=2)
        create_question(category_id="lifestyle", text="質問3", display_order=1)

        result = qna_service.get_all_questions_grouped(test_db_session)

        assert "personality" in result
        assert "lifestyle" in result
        assert len(result["personality"]) == 2
        assert len(result["lifestyle"]) == 1

    def test_get_all_questions(self, test_db_session, create_question):
        create_question(category_id="personality", text="質問1", display_order=2)
        create_question(category_id="lifestyle", text="質問2", display_order=1)

        result = qna_service.get_all_questions(test_db_session)

        assert len(result) == 2
        # display_orderでソートされていることを確認
        assert result[0].display_order == 1
        assert result[1].display_order == 2

    def test_get_questions_by_category(self, test_db_session, create_question):
        create_question(category_id="personality", text="性格質問1")
        create_question(category_id="personality", text="性格質問2")
        create_question(category_id="lifestyle", text="ライフスタイル質問")

        result = qna_service.get_questions_by_category(test_db_session, "personality")

        assert len(result) == 2
        for question in result:
            assert question.category_id == "personality"

    def test_create_answer(self, test_db_session, create_user, create_question):
        user = create_user(user_id="test_user")
        question = create_question()

        answer_data = AnswerCreate(answer_text="これは私の回答です")
        result = qna_service.create_answer(
            test_db_session, user.user_id, question.question_id, answer_data
        )

        assert result.user_id == user.user_id
        assert result.question_id == question.question_id
        assert result.answer_text == "これは私の回答です"
        assert result.answer_id is not None

    def test_get_answer_with_question(
        self, test_db_session, create_user, create_question, create_answer
    ):
        user = create_user(user_id="test_user")
        question = create_question(text="テスト質問")
        answer = create_answer(user.user_id, question.question_id, "テスト回答")

        result = qna_service.get_answer_with_question(test_db_session, answer.answer_id)

        assert result.question.text == "テスト質問"
        assert result.answer.answer_text == "テスト回答"
        assert result.answer.answer_id == answer.answer_id

    def test_get_answer_with_question_not_found(self, test_db_session):
        with pytest.raises(ValueError, match="Answer with id 99999 not found"):
            qna_service.get_answer_with_question(test_db_session, 99999)

    def test_get_answer_with_question_no_question(self, test_db_session, create_user):
        user = create_user(user_id="test_user")

        # 質問なしで直接回答を作成（通常は発生しないが、データ整合性テスト）
        answer = Answer(
            user_id=user.user_id,
            question_id=99999,  # 存在しない質問ID
            answer_text="孤立した回答",
        )
        test_db_session.add(answer)
        test_db_session.commit()
        test_db_session.refresh(answer)

        with pytest.raises(
            ValueError, match=f"Question for answer {answer.answer_id} not found"
        ):
            qna_service.get_answer_with_question(test_db_session, answer.answer_id)

    @patch("src.service.qna_service.get_yaml_loader")
    def test_initialize_default_questions_first_time(
        self, mock_get_loader, test_db_session
    ):
        # モックのYAMLローダーを設定
        mock_loader = Mock()
        mock_template = Mock()
        mock_template.category_id = "personality"
        mock_template.questions = ["質問1", "質問2"]
        mock_loader.load_templates.return_value = [mock_template]
        mock_get_loader.return_value = mock_loader

        qna_service.initialize_default_questions(test_db_session)

        # 質問が作成されたことを確認
        questions = test_db_session.query(Question).all()
        assert len(questions) == 2
        assert questions[0].category_id == "personality"
        assert questions[0].text == "質問1"
        assert questions[0].display_order == 1
        assert questions[1].text == "質問2"
        assert questions[1].display_order == 2

    def test_initialize_default_questions_already_exists(
        self, test_db_session, create_question
    ):
        # 既存の質問を作成
        create_question()

        # 初期化を実行（何もしないはず）
        qna_service.initialize_default_questions(test_db_session)

        # 質問数が変わらないことを確認
        questions = test_db_session.query(Question).all()
        assert len(questions) == 1

    @patch("src.service.qna_service.get_yaml_loader")
    def test_initialize_default_questions_multiple_categories(
        self, mock_get_loader, test_db_session
    ):
        mock_loader = Mock()

        template1 = Mock()
        template1.category_id = "personality"
        template1.questions = ["性格質問1"]

        template2 = Mock()
        template2.category_id = "lifestyle"
        template2.questions = ["ライフスタイル質問1", "ライフスタイル質問2"]

        mock_loader.load_templates.return_value = [template1, template2]
        mock_get_loader.return_value = mock_loader

        qna_service.initialize_default_questions(test_db_session)

        questions = (
            test_db_session.query(Question)
            .order_by(Question.category_id, Question.display_order)
            .all()
        )
        assert len(questions) == 3

        # カテゴリごとに確認
        personality_questions = [q for q in questions if q.category_id == "personality"]
        lifestyle_questions = [q for q in questions if q.category_id == "lifestyle"]

        assert len(personality_questions) == 1
        assert len(lifestyle_questions) == 2
        assert lifestyle_questions[0].display_order == 1
        assert lifestyle_questions[1].display_order == 2

    def test_get_user_qna_with_unanswered_questions(
        self, test_db_session, create_user, create_question, create_answer
    ):
        user = create_user(user_id="test_user")
        question1 = create_question(category_id="personality", text="回答済み質問")
        create_question(category_id="personality", text="未回答質問", display_order=2)

        # 1つの質問にのみ回答
        create_answer(user.user_id, question1.question_id, "回答済み")

        result = qna_service.get_user_qna(test_db_session, user.user_id)

        assert len(result) == 1
        assert len(result[0].answers) == 2  # 全質問が含まれる

        # 回答状況を確認
        answered = [a for a in result[0].answers if a.answer_text]
        unanswered = [a for a in result[0].answers if not a.answer_text]

        assert len(answered) == 1
        assert len(unanswered) == 1
        assert unanswered[0].answer_id == 0  # 未回答の場合のデフォルト値
