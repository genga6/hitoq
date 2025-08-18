import pytest

from src.service.categories import (
    CATEGORIES,
    CategoryInfo,
    get_all_categories,
    get_categories_dict,
    get_category_by_id,
    get_category_by_name,
    get_category_names_dict,
    is_valid_category_id,
    is_valid_category_name,
)


@pytest.mark.unit
class TestCategories:
    def test_get_all_categories_returns_list(self):
        categories = get_all_categories()

        assert isinstance(categories, list)
        assert len(categories) > 0

        for category in categories:
            assert isinstance(category, CategoryInfo)
            assert hasattr(category, "id")
            assert hasattr(category, "name")
            assert hasattr(category, "description")

    def test_get_all_categories_contains_expected_categories(self):
        categories = get_all_categories()
        category_ids = [cat.id for cat in categories]

        # 最低限含まれるべきカテゴリ
        expected_categories = ["personality", "lifestyle", "relationships"]

        for expected in expected_categories:
            assert expected in category_ids

    def test_get_all_categories_returns_copy(self):
        categories1 = get_all_categories()
        categories2 = get_all_categories()

        assert categories1 is not categories2
        assert categories1 == categories2

    def test_get_category_by_id_success(self):
        category = get_category_by_id("personality")

        assert category is not None
        assert category.id == "personality"
        assert category.name == "性格・特徴"
        assert "性格" in category.description

    def test_get_category_by_id_not_found(self):
        category = get_category_by_id("nonexistent_id")

        assert category is None

    def test_get_category_by_name_success(self):
        category = get_category_by_name("性格・特徴")

        assert category is not None
        assert category.id == "personality"
        assert category.name == "性格・特徴"

    def test_get_category_by_name_not_found(self):
        category = get_category_by_name("存在しないカテゴリ")

        assert category is None

    def test_get_categories_dict(self):
        categories_dict = get_categories_dict()

        assert isinstance(categories_dict, dict)
        assert len(categories_dict) == len(CATEGORIES)

        assert "personality" in categories_dict
        assert "lifestyle" in categories_dict
        assert "relationships" in categories_dict

        for category_id, category_info in categories_dict.items():
            assert isinstance(category_info, CategoryInfo)
            assert category_info.id == category_id

    def test_get_category_names_dict(self):
        names_dict = get_category_names_dict()

        assert isinstance(names_dict, dict)
        assert len(names_dict) == len(CATEGORIES)

        assert names_dict["personality"] == "性格・特徴"
        assert names_dict["lifestyle"] == "ライフスタイル"
        assert names_dict["relationships"] == "人間関係"

    def test_is_valid_category_id_valid(self):
        valid_ids = ["personality", "lifestyle", "relationships", "romance"]

        for category_id in valid_ids:
            assert is_valid_category_id(category_id) is True

    def test_is_valid_category_id_invalid(self):
        invalid_ids = ["invalid_id", "nonexistent", "", "PERSONALITY"]

        for category_id in invalid_ids:
            assert is_valid_category_id(category_id) is False

    def test_is_valid_category_name_valid(self):
        valid_names = ["性格・特徴", "ライフスタイル", "人間関係", "恋愛"]

        for category_name in valid_names:
            assert is_valid_category_name(category_name) is True

    def test_is_valid_category_name_invalid(self):
        invalid_names = ["無効な名前", "存在しない", "", "personality"]

        for category_name in invalid_names:
            assert is_valid_category_name(category_name) is False

    def test_category_info_dataclass(self):
        category = CategoryInfo(
            id="test_id", name="テストカテゴリ", description="テスト用の説明"
        )

        assert category.id == "test_id"
        assert category.name == "テストカテゴリ"
        assert category.description == "テスト用の説明"

    def test_categories_constant_immutability(self):
        original_length = len(CATEGORIES)

        original_categories = CATEGORIES.copy()

        returned_categories = get_all_categories()
        returned_categories.append(CategoryInfo("fake", "偽", "偽のカテゴリ"))

        assert len(CATEGORIES) == original_length
        assert CATEGORIES == original_categories

    @pytest.mark.parametrize(
        "category_id,expected_name",
        [
            ("values", "価値観"),
            ("personality", "性格・特徴"),
            ("relationships", "人間関係"),
            ("romance", "恋愛"),
            ("childhood", "子供時代"),
            ("school", "学生時代"),
            ("career", "キャリア"),
            ("lifestyle", "ライフスタイル"),
        ],
    )
    def test_category_id_name_mapping(self, category_id, expected_name):
        category = get_category_by_id(category_id)

        assert category is not None
        assert category.name == expected_name
