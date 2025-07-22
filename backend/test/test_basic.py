from fastapi.testclient import TestClient


class TestBasicEndpoints:
    def test_root_endpoint(self, client: TestClient):
        """ルートエンドポイントのテスト"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to hitoQ API!"}

    def test_health_endpoint(self, client: TestClient):
        """ヘルスチェックエンドポイントのテスト"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_user_creation_workflow(self, client: TestClient):
        """ユーザー作成ワークフローのテスト"""
        user_data = {
            "user_id": "workflow_user",
            "user_name": "workflowuser",
            "display_name": "Workflow User",
            "bio": "Testing workflow",
            "icon_url": "https://example.com/workflow.jpg",
        }

        # ユーザー作成
        response = client.post("/users", json=user_data)
        assert response.status_code == 201

        created_user = response.json()
        assert created_user["userId"] == user_data["user_id"]
        assert created_user["userName"] == user_data["user_name"]
        assert created_user["displayName"] == user_data["display_name"]

        # 作成したユーザーを取得
        response = client.get(f"/users/{user_data['user_id']}")
        assert response.status_code == 200

        retrieved_user = response.json()
        assert retrieved_user["userId"] == user_data["user_id"]

    def test_profile_item_workflow(self, client: TestClient):
        """プロフィールアイテム作成ワークフローのテスト"""
        # まずユーザーを作成
        user_data = {
            "user_id": "profile_user",
            "user_name": "profileuser",
            "display_name": "Profile User",
            "bio": "Testing profile",
            "icon_url": "https://example.com/profile.jpg",
        }

        user_response = client.post("/users", json=user_data)
        assert user_response.status_code == 201

        # プロフィールアイテムを作成
        profile_item_data = {
            "label": "Hobby",
            "value": "Reading books",
            "display_order": 1,
        }

        item_response = client.post(
            f"/users/{user_data['user_id']}/profile-items", json=profile_item_data
        )
        assert item_response.status_code == 201

        item = item_response.json()
        assert item["label"] == profile_item_data["label"]
        assert item["value"] == profile_item_data["value"]
        assert item["userId"] == user_data["user_id"]

    def test_bucket_list_item_workflow(self, client: TestClient):
        """バケットリストアイテム作成ワークフローのテスト"""
        # まずユーザーを作成
        user_data = {
            "user_id": "bucket_user",
            "user_name": "bucketuser",
            "display_name": "Bucket User",
            "bio": "Testing bucket list",
            "icon_url": "https://example.com/bucket.jpg",
        }

        user_response = client.post("/users", json=user_data)
        assert user_response.status_code == 201

        # バケットリストアイテムを作成
        bucket_item_data = {
            "content": "Visit Tokyo",
            "is_completed": False,
            "display_order": 1,
        }

        item_response = client.post(
            f"/users/{user_data['user_id']}/bucket-list-items", json=bucket_item_data
        )
        assert item_response.status_code == 201

        item = item_response.json()
        assert item["content"] == bucket_item_data["content"]
        assert item["isCompleted"] == bucket_item_data["is_completed"]
        assert item["userId"] == user_data["user_id"]

        # アイテムを完了に変更
        item_id = item["bucketListItemId"]
        update_data = {
            "content": "Visit Tokyo",
            "is_completed": True,
            "display_order": 1,
        }

        update_response = client.put(
            f"/users/{user_data['user_id']}/bucket-list-items/{item_id}",
            json=update_data,
        )
        assert update_response.status_code == 200

        updated_item = update_response.json()
        assert updated_item["isCompleted"]

    def test_page_data_endpoints(self, client: TestClient):
        """ページデータエンドポイントのテスト"""
        # ユーザーを作成
        user_data = {
            "user_id": "page_user",
            "user_name": "pageuser",
            "display_name": "Page User",
            "bio": "Testing page data",
            "icon_url": "https://example.com/page.jpg",
        }

        user_response = client.post("/users", json=user_data)
        assert user_response.status_code == 201

        username = user_data["user_name"]

        # プロフィールページデータ取得
        profile_response = client.get(f"/users/by-username/{username}/profile")
        assert profile_response.status_code == 200

        profile_data = profile_response.json()
        assert "profile" in profile_data
        assert "profileItems" in profile_data
        assert profile_data["profile"]["userId"] == user_data["user_id"]

        # バケットリストページデータ取得
        bucket_response = client.get(f"/users/by-username/{username}/bucket-list")
        assert bucket_response.status_code == 200

        bucket_data = bucket_response.json()
        assert "profile" in bucket_data
        assert "bucketListItems" in bucket_data
        assert bucket_data["profile"]["userId"] == user_data["user_id"]

        # Q&Aページデータ取得
        qna_response = client.get(f"/users/by-username/{username}/qna")
        assert qna_response.status_code == 200

        qna_data = qna_response.json()
        assert "profile" in qna_data
        assert "userAnswerGroups" in qna_data
        assert "availableTemplates" in qna_data
        assert qna_data["profile"]["userId"] == user_data["user_id"]
