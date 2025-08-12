"""
Q&Aサービスのユニットテスト
"""

from unittest.mock import Mock, patch

import pytest

from src.db.tables import Answer, Question
from src.schema.answer import AnswerCreate
from src.schema.question import QuestionCreate
from src.service.qna_service import QNAService


class TestQNAService:
    @pytest.fixture
    def mock_session(self):
        return Mock()

    @pytest.fixture
    def qna_service(self):
        return QNAService()

    def test_create_question_success(self, qna_service, mock_session):
        """質問作成成功"""
        question_data = QuestionCreate(
            content="テスト質問", category="general", user_id=1
        )

        created_question = Question(id=1, **question_data.dict())

        with patch("src.service.qna_service.Question", return_value=created_question):
            result = qna_service.create_question(mock_session, question_data)

        assert result.content == "テスト質問"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.parametrize("category", ["general", "personal", "work", "hobby"])
    def test_get_questions_by_category(self, qna_service, mock_session, category):
        """カテゴリ別質問取得"""
        mock_questions = [
            Question(id=1, category=category, content="質問1"),
            Question(id=2, category=category, content="質問2"),
        ]
        mock_session.query().filter().all.return_value = mock_questions

        result = qna_service.get_questions_by_category(mock_session, category)

        assert len(result) == 2
        assert all(q.category == category for q in result)

    def test_create_answer(self, qna_service, mock_session):
        """回答作成"""
        answer_data = AnswerCreate(content="テスト回答", question_id=1, user_id=1)

        created_answer = Answer(id=1, **answer_data.dict())

        with patch("src.service.qna_service.Answer", return_value=created_answer):
            result = qna_service.create_answer(mock_session, answer_data)

        assert result.content == "テスト回答"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.parametrize(
        "content,valid",
        [("有効な回答", True), ("", False), ("A" * 1000, True), ("A" * 10001, False)],
    )
    def test_validate_answer_content(self, qna_service, content, valid):
        """回答内容検証"""
        result = qna_service._validate_answer_content(content)
        assert result == valid
