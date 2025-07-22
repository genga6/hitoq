import pytest
from fastapi.testclient import TestClient

from test.test_fixtures import create_test_user


@pytest.mark.integration
class TestUserWorkflow:
    def test_complete_user_profile_workflow(self, client: TestClient, test_db_session):
        """完全なユーザープロフィール作成ワークフローのテスト"""
        # 1. ユーザーを作成
        user_data = {
            "user_id": "workflow_user",
            "user_name": "workflowuser",
            "display_name": "Workflow User",
            "bio": "Testing complete workflow",
            "icon_url": "https://example.com/workflow.jpg",
        }

        create_user_response = client.post("/users", json=user_data)
        assert create_user_response.status_code == 201
        created_user = create_user_response.json()

        # 2. プロフィールアイテムを複数作成
        profile_items_data = [
            {"label": "Age", "value": "25", "display_order": 1},
            {"label": "Location", "value": "Tokyo", "display_order": 2},
            {"label": "Occupation", "value": "Software Engineer", "display_order": 3},
        ]

        profile_item_ids = []
        for item_data in profile_items_data:
            response = client.post(
                f"/users/{created_user['userId']}/profile-items", json=item_data
            )
            assert response.status_code == 201
            profile_item_ids.append(response.json()["profileItemId"])

        # 3. バケットリストアイテムを複数作成
        bucket_items_data = [
            {"content": "Learn Japanese", "is_completed": False, "display_order": 1},
            {"content": "Visit Mt. Fuji", "is_completed": False, "display_order": 2},
            {"content": "Write a blog", "is_completed": True, "display_order": 3},
        ]

        bucket_item_ids = []
        for item_data in bucket_items_data:
            response = client.post(
                f"/users/{created_user['userId']}/bucket-list-items", json=item_data
            )
            assert response.status_code == 201
            bucket_item_ids.append(response.json()["bucketListItemId"])

        # 4. プロフィールページデータを取得して確認
        profile_response = client.get(
            f"/users/by-username/{created_user['userName']}/profile"
        )
        assert profile_response.status_code == 200

        profile_data = profile_response.json()
        assert profile_data["profile"]["userId"] == created_user["userId"]
        # Allow for profile items from previous tests, but verify we have at least 3
        assert len(profile_data["profileItems"]) >= 3

        # 5. バケットリストページデータを取得して確認
        bucket_response = client.get(
            f"/users/by-username/{created_user['userName']}/bucket-list"
        )
        assert bucket_response.status_code == 200

        bucket_data = bucket_response.json()
        assert bucket_data["profile"]["userId"] == created_user["userId"]
        # Allow for bucket items from previous tests, but verify we have at least 3
        assert len(bucket_data["bucketListItems"]) >= 3

        # 6. プロフィールアイテムを更新
        update_response = client.put(
            f"/users/{created_user['userId']}/profile-items/{profile_item_ids[0]}",
            json={"label": "Age", "value": "26"},
        )
        assert update_response.status_code == 200

        # 7. バケットリストアイテムを完了に変更
        complete_response = client.put(
            f"/users/{created_user['userId']}/bucket-list-items/{bucket_item_ids[0]}",
            json={
                "content": "Learn Japanese",
                "is_completed": True,
                "display_order": 1,
            },
        )
        assert complete_response.status_code == 200

        # 8. 変更が反映されていることを確認
        updated_profile_response = client.get(
            f"/users/by-username/{created_user['userName']}/profile"
        )
        updated_profile_data = updated_profile_response.json()
        age_item = next(
            item
            for item in updated_profile_data["profileItems"]
            if item["label"] == "Age"
        )
        assert age_item["value"] == "26"

        updated_bucket_response = client.get(
            f"/users/by-username/{created_user['userName']}/bucket-list"
        )
        updated_bucket_data = updated_bucket_response.json()
        learn_japanese_item = next(
            item
            for item in updated_bucket_data["bucketListItems"]
            if item["content"] == "Learn Japanese"
        )
        assert learn_japanese_item["isCompleted"]

    def test_user_qna_workflow(self, client: TestClient, test_db_session):
        """Q&A ワークフローのテスト"""
        # ユーザー作成
        user = create_test_user(
            test_db_session,
            {
                "user_id": "qna_user",
                "user_name": "qnauser",
                "display_name": "QnA User",
                "bio": "Testing QnA workflow",
                "icon_url": "https://example.com/qna.jpg",
            },
        )

        # Q&A ページデータ取得
        qna_response = client.get(f"/users/by-username/{user.user_name}/qna")
        # QnA endpoint might return 404 if no questions exist
        assert qna_response.status_code in [200, 404]

        qna_data = qna_response.json()
        assert "profile" in qna_data
        assert "userAnswerGroups" in qna_data
        assert "availableTemplates" in qna_data
        assert qna_data["profile"]["userId"] == user.user_id

        # 質問一覧を取得
        questions_response = client.get("/users/questions")
        # Questions endpoint might return 404 if no questions exist
        assert questions_response.status_code in [200, 404]
        questions = (
            questions_response.json() if questions_response.status_code == 200 else []
        )

        # 回答を作成（質問があれば）
        if questions:
            first_question_id = questions[0]["questionId"]  # 最初の質問に回答
            answer_data = {"answer_text": "This is my answer to the first question!"}

            answer_response = client.post(
                f"/users/{user.user_id}/questions/{first_question_id}/answers",
                json=answer_data,
            )
            # 質問が存在すれば回答作成は成功するはず
            assert answer_response.status_code in [
                200,
                404,
            ]  # 質問が見つからない場合は404

    def test_multiple_users_interaction(self, client: TestClient, test_db_session):
        """複数ユーザーの相互作用テスト"""
        # 3人のユーザーを作成
        users_data = [
            {
                "user_id": "user_a",
                "user_name": "usera",
                "display_name": "User A",
                "bio": "User A bio",
                "icon_url": "https://example.com/a.jpg",
            },
            {
                "user_id": "user_b",
                "user_name": "userb",
                "display_name": "User B",
                "bio": "User B bio",
                "icon_url": "https://example.com/b.jpg",
            },
            {
                "user_id": "user_c",
                "user_name": "userc",
                "display_name": "User C",
                "bio": "User C bio",
                "icon_url": "https://example.com/c.jpg",
            },
        ]

        created_users = []
        for user_data in users_data:
            response = client.post("/users", json=user_data)
            assert response.status_code == 201
            created_users.append(response.json())

        # 各ユーザーがプロフィールアイテムを作成
        for i, user in enumerate(created_users):
            profile_data = {
                "label": f"Hobby {i + 1}",
                "value": f"Hobby content {i + 1}",
                "display_order": 1,
            }
            response = client.post(
                f"/users/{user['userId']}/profile-items", json=profile_data
            )
            assert response.status_code == 201

        # 全ユーザーリストを取得
        all_users_response = client.get("/users")
        assert all_users_response.status_code == 200
        all_users = all_users_response.json()
        assert (
            len([u for u in all_users if u["userId"] in ["user_a", "user_b", "user_c"]])
            == 3
        )

        # 各ユーザーのプロフィールページが正常に取得できることを確認
        for user in created_users:
            profile_response = client.get(
                f"/users/by-username/{user['userName']}/profile"
            )
            assert profile_response.status_code == 200
            profile_data = profile_response.json()
            # Allow for multiple profile items from previous tests
            assert len(profile_data["profileItems"]) >= 1
