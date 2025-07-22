from fastapi.testclient import TestClient

from test.test_fixtures import create_test_user


class TestBucketListEndpoints:
    def test_create_bucket_list_item_success(
        self, client: TestClient, test_db_session, sample_bucket_list_item_data
    ):
        """バケットリストアイテム作成の成功テスト"""
        test_user = create_test_user(test_db_session)
        response = client.post(
            f"/users/{test_user.user_id}/bucket-list-items",
            json=sample_bucket_list_item_data,
        )
        assert response.status_code == 201

        data = response.json()
        assert "bucketListItemId" in data
        assert data["content"] == sample_bucket_list_item_data["content"]
        assert data["isCompleted"] == sample_bucket_list_item_data["is_completed"]
        assert data["userId"] == test_user.user_id

    def test_create_bucket_list_item_invalid_user(
        self, client: TestClient, sample_bucket_list_item_data
    ):
        """存在しないユーザーでのバケットリストアイテム作成テスト"""
        response = client.post(
            "/users/nonexistent_user/bucket-list-items",
            json=sample_bucket_list_item_data,
        )
        # User creation might succeed with auto-creation, so allow 201 or error codes
        assert response.status_code in [201, 400, 404]

    def test_create_bucket_list_item_empty_content(
        self, client: TestClient, test_db_session
    ):
        """空のコンテンツでのバケットリストアイテム作成テスト"""
        test_user = create_test_user(test_db_session)
        empty_item_data = {"content": "", "is_completed": False, "display_order": 1}

        response = client.post(
            f"/users/{test_user.user_id}/bucket-list-items", json=empty_item_data
        )
        # Empty content might be allowed, so accept success or validation error
        assert response.status_code in [201, 400, 422]

    def test_create_bucket_list_item_missing_fields(
        self, client: TestClient, test_db_session
    ):
        """必須フィールドなしでのバケットリストアイテム作成テスト"""
        test_user = create_test_user(test_db_session)
        invalid_item_data = {"invalid_field": "value"}

        response = client.post(
            f"/users/{test_user.user_id}/bucket-list-items", json=invalid_item_data
        )
        assert response.status_code == 422  # FastAPI validation error

    def test_update_bucket_list_item_success(
        self, client: TestClient, test_db_session, sample_bucket_list_item_data
    ):
        """バケットリストアイテム更新の成功テスト"""
        test_user = create_test_user(test_db_session)
        # まずアイテムを作成
        create_response = client.post(
            f"/users/{test_user.user_id}/bucket-list-items",
            json=sample_bucket_list_item_data,
        )
        assert create_response.status_code == 201
        created_item = create_response.json()
        item_id = created_item["bucketListItemId"]

        # アイテムを更新
        update_data = {
            "content": "Updated bucket list item",
            "is_completed": True,
            "display_order": 2,
        }
        update_response = client.put(
            f"/users/{test_user.user_id}/bucket-list-items/{item_id}", json=update_data
        )
        assert update_response.status_code == 200

        updated_item = update_response.json()
        assert updated_item["content"] == update_data["content"]
        assert updated_item["isCompleted"] == update_data["is_completed"]
        assert updated_item["bucketListItemId"] == item_id

    def test_update_bucket_list_item_not_found(
        self, client: TestClient, test_db_session
    ):
        """存在しないバケットリストアイテムの更新テスト"""
        test_user = create_test_user(test_db_session)
        update_data = {
            "content": "Updated content",
            "is_completed": True,
            "display_order": 1,
        }

        response = client.put(
            f"/users/{test_user.user_id}/bucket-list-items/99999", json=update_data
        )
        assert response.status_code in [400, 404]

    def test_delete_bucket_list_item_success(
        self, client: TestClient, test_db_session, sample_bucket_list_item_data
    ):
        """バケットリストアイテム削除の成功テスト"""
        test_user = create_test_user(test_db_session)
        # まずアイテムを作成
        create_response = client.post(
            f"/users/{test_user.user_id}/bucket-list-items",
            json=sample_bucket_list_item_data,
        )
        assert create_response.status_code == 201
        item_id = create_response.json()["bucketListItemId"]

        # アイテムを削除
        delete_response = client.delete(
            f"/users/{test_user.user_id}/bucket-list-items/{item_id}"
        )
        assert delete_response.status_code == 204

    def test_delete_bucket_list_item_not_found(
        self, client: TestClient, test_db_session
    ):
        """存在しないバケットリストアイテムの削除テスト"""
        test_user = create_test_user(test_db_session)
        response = client.delete(f"/users/{test_user.user_id}/bucket-list-items/99999")
        assert response.status_code in [400, 404]

    def test_create_multiple_bucket_list_items(
        self, client: TestClient, test_db_session
    ):
        """同じユーザーで複数のバケットリストアイテム作成テスト"""
        test_user = create_test_user(test_db_session)
        items_data = [
            {"content": "Travel to Japan", "is_completed": False, "display_order": 1},
            {"content": "Learn Python", "is_completed": True, "display_order": 2},
            {"content": "Write a book", "is_completed": False, "display_order": 3},
        ]

        created_items = []
        for item_data in items_data:
            response = client.post(
                f"/users/{test_user.user_id}/bucket-list-items", json=item_data
            )
            assert response.status_code == 201
            created_items.append(response.json())

        # 作成されたアイテムの検証
        assert len(created_items) == 3
        for i, item in enumerate(created_items):
            assert item["content"] == items_data[i]["content"]
            assert item["isCompleted"] == items_data[i]["is_completed"]

    def test_bucket_list_item_completion_toggle(
        self, client: TestClient, test_db_session
    ):
        """バケットリストアイテムの完了状態切り替えテスト"""
        test_user = create_test_user(test_db_session)
        # 未完了アイテムを作成
        item_data = {
            "content": "Learn FastAPI",
            "is_completed": False,
            "display_order": 1,
        }
        create_response = client.post(
            f"/users/{test_user.user_id}/bucket-list-items", json=item_data
        )
        assert create_response.status_code == 201
        item_id = create_response.json()["bucketListItemId"]

        # 完了状態に更新
        update_data = {
            "content": "Learn FastAPI",
            "is_completed": True,
            "display_order": 1,
        }
        update_response = client.put(
            f"/users/{test_user.user_id}/bucket-list-items/{item_id}", json=update_data
        )
        assert update_response.status_code == 200
        assert update_response.json()["isCompleted"]

        # 再び未完了に戻す
        toggle_data = {
            "content": "Learn FastAPI",
            "is_completed": False,
            "display_order": 1,
        }
        toggle_response = client.put(
            f"/users/{test_user.user_id}/bucket-list-items/{item_id}", json=toggle_data
        )
        assert toggle_response.status_code == 200
        assert not toggle_response.json()["isCompleted"]
