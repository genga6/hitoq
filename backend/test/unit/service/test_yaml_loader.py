from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
import yaml

from src.service.yaml_loader import (
    QuestionTemplate,
    YamlTemplateLoader,
    get_yaml_loader,
    load_default_labels,
)


@pytest.mark.unit
class TestQuestionTemplate:
    def test_question_template_creation(self):
        template = QuestionTemplate(
            category_id="personality",
            category_name="性格・特徴",
            questions=["質問1", "質問2"],
        )

        assert template.category_id == "personality"
        assert template.category_name == "性格・特徴"
        assert template.questions == ["質問1", "質問2"]


@pytest.mark.unit
class TestYamlTemplateLoader:
    def test_yaml_loader_initialization_default(self):
        loader = YamlTemplateLoader()

        expected_path = (
            Path(__file__).parent.parent.parent.parent
            / "src"
            / "config"
            / "question_templates"
        )
        assert loader.config_dir == expected_path
        assert loader._templates_cache is None

    def test_yaml_loader_initialization_custom_dir(self, temp_config_dir):
        loader = YamlTemplateLoader(temp_config_dir)

        assert loader.config_dir == temp_config_dir

    def test_load_yaml_file_success(self, temp_config_dir, sample_yaml_content):
        loader = YamlTemplateLoader(temp_config_dir)
        yaml_file = temp_config_dir / "test.yaml"

        with open(yaml_file, "w", encoding="utf-8") as f:
            yaml.dump(sample_yaml_content, f, allow_unicode=True)

        result = loader._load_yaml_file(yaml_file)

        assert result == sample_yaml_content

    def test_load_yaml_file_not_found(self, temp_config_dir):
        loader = YamlTemplateLoader(temp_config_dir)
        nonexistent_file = temp_config_dir / "nonexistent.yaml"

        with pytest.raises(RuntimeError, match="Failed to load YAML file"):
            loader._load_yaml_file(nonexistent_file)

    @patch("src.service.yaml_loader.get_category_by_name")
    def test_parse_template_success(self, mock_get_category, sample_yaml_content):
        mock_category = type(
            "Category", (), {"id": "personality", "name": "性格・特徴"}
        )()
        mock_get_category.return_value = mock_category

        loader = YamlTemplateLoader()
        result = loader._parse_template(sample_yaml_content, "test.yaml")

        assert isinstance(result, QuestionTemplate)
        assert result.category_id == "personality"
        assert result.category_name == "性格・特徴"
        assert len(result.questions) == 3

    @patch("src.service.yaml_loader.get_category_by_name")
    def test_parse_template_unknown_category(
        self, mock_get_category, sample_yaml_content
    ):
        mock_get_category.return_value = None

        loader = YamlTemplateLoader()

        with pytest.raises(RuntimeError, match="Unknown category"):
            loader._parse_template(sample_yaml_content, "test.yaml")

    def test_parse_template_missing_category(self):
        invalid_data = {"questions": ["質問1"]}  # categoryフィールドなし

        loader = YamlTemplateLoader()

        with pytest.raises(RuntimeError, match="Missing 'category' field"):
            loader._parse_template(invalid_data, "test.yaml")

    def test_parse_template_missing_questions(self):
        invalid_data = {"category": "性格・特徴"}  # questionsフィールドなし

        loader = YamlTemplateLoader()

        with pytest.raises(RuntimeError, match="Missing 'questions' field"):
            loader._parse_template(invalid_data, "test.yaml")

    @patch("src.service.yaml_loader.get_category_by_name")
    def test_load_templates_success(
        self, mock_get_category, temp_config_dir, sample_yaml_content
    ):
        mock_category = type(
            "Category", (), {"id": "personality", "name": "性格・特徴"}
        )()
        mock_get_category.return_value = mock_category

        # テスト用YAMLファイルを作成
        yaml_file = temp_config_dir / "personality.yaml"
        with open(yaml_file, "w", encoding="utf-8") as f:
            yaml.dump(sample_yaml_content, f, allow_unicode=True)

        loader = YamlTemplateLoader(temp_config_dir)
        result = loader.load_templates()

        assert len(result) == 1
        assert result[0].category_id == "personality"
        assert len(result[0].questions) == 3

    def test_load_templates_directory_not_found(self):
        nonexistent_dir = Path("/nonexistent/directory")
        loader = YamlTemplateLoader(nonexistent_dir)

        with pytest.raises(RuntimeError, match="Configuration directory not found"):
            loader.load_templates()

    def test_load_templates_no_yaml_files(self, temp_config_dir):
        loader = YamlTemplateLoader(temp_config_dir)

        with pytest.raises(RuntimeError, match="No YAML files found"):
            loader.load_templates()

    @patch("src.service.yaml_loader.get_category_by_name")
    def test_load_templates_multiple_files(self, mock_get_category, temp_config_dir):
        # 2つの異なるカテゴリのモックを設定
        def get_category_side_effect(category_name):
            if category_name == "性格・特徴":
                return type(
                    "Category", (), {"id": "personality", "name": "性格・特徴"}
                )()
            elif category_name == "ライフスタイル":
                return type(
                    "Category", (), {"id": "lifestyle", "name": "ライフスタイル"}
                )()
            return None

        mock_get_category.side_effect = get_category_side_effect

        # 2つのYAMLファイルを作成
        yaml1_content = {"category": "性格・特徴", "questions": ["性格質問1"]}
        yaml2_content = {
            "category": "ライフスタイル",
            "questions": ["ライフスタイル質問1", "ライフスタイル質問2"],
        }

        with open(temp_config_dir / "personality.yaml", "w", encoding="utf-8") as f:
            yaml.dump(yaml1_content, f, allow_unicode=True)
        with open(temp_config_dir / "lifestyle.yml", "w", encoding="utf-8") as f:
            yaml.dump(yaml2_content, f, allow_unicode=True)

        loader = YamlTemplateLoader(temp_config_dir)
        result = loader.load_templates()

        assert len(result) == 2
        category_ids = [template.category_id for template in result]
        assert "personality" in category_ids
        assert "lifestyle" in category_ids

    @patch("src.service.yaml_loader.get_category_by_name")
    def test_get_templates_caching(
        self, mock_get_category, temp_config_dir, sample_yaml_content
    ):
        mock_category = type(
            "Category", (), {"id": "personality", "name": "性格・特徴"}
        )()
        mock_get_category.return_value = mock_category

        yaml_file = temp_config_dir / "test.yaml"
        with open(yaml_file, "w", encoding="utf-8") as f:
            yaml.dump(sample_yaml_content, f, allow_unicode=True)

        loader = YamlTemplateLoader(temp_config_dir)

        # 最初の呼び出し
        result1 = loader.get_templates()
        # 2回目の呼び出し
        result2 = loader.get_templates()

        assert result1 == result2
        assert loader._templates_cache is not None
        # load_templatesは1回だけ呼ばれる（キャッシュされている）


@pytest.mark.unit
class TestGlobalFunctions:
    def test_get_yaml_loader_singleton(self):
        loader1 = get_yaml_loader()
        loader2 = get_yaml_loader()

        assert loader1 is loader2
        assert isinstance(loader1, YamlTemplateLoader)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="profile_labels:\n  - ラベル1\n  - ラベル2\n",
    )
    @patch("yaml.safe_load")
    def test_load_default_labels_success(self, mock_yaml_load, mock_file):
        mock_yaml_load.return_value = {"profile_labels": ["ラベル1", "ラベル2"]}

        result = load_default_labels()

        assert result == ["ラベル1", "ラベル2"]
        mock_file.assert_called_once()

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_default_labels_fallback(self, _mock_file):
        result = load_default_labels()

        # デフォルトのラベルが返される
        assert isinstance(result, list)
        assert len(result) > 0
        assert "趣味・今ハマっていること" in result

    @patch("builtins.open", new_callable=mock_open, read_data="invalid yaml content")
    @patch("yaml.safe_load", side_effect=yaml.YAMLError("YAML parse error"))
    def test_load_default_labels_yaml_error(self, _mock_yaml_load, _mock_file):
        result = load_default_labels()

        # エラー時はデフォルトラベルが返される
        assert isinstance(result, list)
        assert "趣味・今ハマっていること" in result

    @patch("builtins.open", new_callable=mock_open, read_data="other_field: value")
    @patch("yaml.safe_load")
    def test_load_default_labels_missing_field(self, mock_yaml_load, _mock_file):
        mock_yaml_load.return_value = {
            "other_field": "value"
        }  # profile_labelsフィールドなし

        result = load_default_labels()

        # profile_labelsがない場合は空リストが返される
        assert result == []
