import pytest
from fastapi import status

# Answer クラスのimportは不要（create_answerヘルパーを使用）


@pytest.mark.integration
class TestQnARouter:
    def test_create_answer_success(
        self, client, test_db_session, create_user, create_question, csrf_headers
    ):
        user = create_user(user_id="answer_user", user_name="answeruser")
        question = create_question(text="テスト質問です", category_id="personality")

        answer_data = {"answer_text": "これは私の回答です。"}

        response = client.post(
            f"/users/{user.user_id}/questions/{question.question_id}/answers",
            json=answer_data,
            headers=csrf_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert response_data["answerText"] == "これは私の回答です。"
        assert response_data["userId"] == user.user_id
        assert response_data["questionId"] == question.question_id

    def test_create_answer_nonexistent_user(
        self, client, create_question, csrf_headers
    ):
        question = create_question(text="テスト質問", category_id="personality")

        answer_data = {"answer_text": "存在しないユーザーの回答"}

        # NOTE: `nonexistent_user`というuser_idになってしまうため認証チェックしている
        response = client.post(
            f"/users/nonexistent_user/questions/{question.question_id}/answers",
            json=answer_data,
            headers=csrf_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_answer_nonexistent_question(
        self, client, create_user, csrf_headers
    ):
        user = create_user(user_id="test_user", user_name="testuser")

        answer_data = {"answer_text": "存在しない質問への回答"}

        response = client.post(
            f"/users/{user.user_id}/questions/99999/answers",
            json=answer_data,
            headers=csrf_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_answer_duplicate(
        self,
        client,
        test_db_session,
        create_user,
        create_question,
        create_answer,
        csrf_headers,
    ):
        user = create_user(user_id="dup_user", user_name="dupuser")
        question = create_question(text="重複テスト質問", category_id="personality")

        # 既存の回答をcreate_answerヘルパーで作成
        create_answer(user.user_id, question.question_id, "既存の回答")

        answer_data = {"answer_text": "新しい回答"}

        response = client.post(
            f"/users/{user.user_id}/questions/{question.question_id}/answers",
            json=answer_data,
            headers=csrf_headers,
        )

        assert response.status_code in [status.HTTP_409_CONFLICT, status.HTTP_200_OK]

    def test_create_answer_empty_text_allowed(
        self, client, create_user, create_question, csrf_headers
    ):
        user = create_user(user_id="empty_answer_user", user_name="emptyuser")
        question = create_question(text="空回答テスト", category_id="personality")

        empty_answer_data = {"answer_text": ""}

        response = client.post(
            f"/users/{user.user_id}/questions/{question.question_id}/answers",
            json=empty_answer_data,
            headers=csrf_headers,
        )

        # 空の回答も許容される
        assert response.status_code == status.HTTP_200_OK

    def test_read_all_questions_success(self, client, test_db_session, create_question):
        [
            create_question(text="質問1", category_id="personality"),
            create_question(text="質問2", category_id="lifestyle"),
            create_question(text="質問3", category_id="personality"),
        ]

        response = client.get("/questions/")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert isinstance(response_data, list)
        assert len(response_data) >= 3

        question_texts = [q["text"] for q in response_data]
        assert "質問1" in question_texts
        assert "質問2" in question_texts
        assert "質問3" in question_texts

    def test_read_questions_by_category_success(self, client, create_question):
        [
            create_question(text="性格質問1", category_id="personality"),
            create_question(text="性格質問2", category_id="personality"),
        ]
        create_question(text="ライフスタイル質問", category_id="lifestyle")

        response = client.get("/questions/by-category/personality")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert isinstance(response_data, list)
        assert len(response_data) >= 2

        for question in response_data:
            assert question["categoryId"] == "personality"

    def test_read_questions_by_nonexistent_category(self, client):
        response = client.get("/questions/by-category/nonexistent_category")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert isinstance(response_data, list)
        assert len(response_data) == 0

    def test_read_categories_success(self, client):
        response = client.get("/questions/categories")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert isinstance(response_data, list)
        assert len(response_data) > 0

        for category in response_data:
            assert "id" in category
            assert "name" in category
            assert isinstance(category["id"], str)
            assert isinstance(category["name"], str)

    def test_answer_text_length_validation(
        self, client, create_user, create_question, csrf_headers
    ):
        user = create_user(user_id="length_user", user_name="lengthuser")
        question = create_question(text="長さテスト質問", category_id="personality")

        very_long_text = "A" * 10000

        answer_data = {"answer_text": very_long_text}

        response = client.post(
            f"/users/{user.user_id}/questions/{question.question_id}/answers",
            json=answer_data,
            headers=csrf_headers,
        )

        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_200_OK,
        ]
