from dataclasses import dataclass
from pathlib import Path

import yaml

from src.service.categories import get_category_by_name


@dataclass
class QuestionTemplate:
    category_id: str
    category_name: str
    questions: list[str]


class YamlTemplateLoader:
    def __init__(self, config_dir: str | Path | None = None):
        if config_dir is None:
            current_dir = Path(__file__).parent.parent
            self.config_dir = current_dir / "config" / "question_templates"
        else:
            self.config_dir = Path(config_dir)
        self._templates_cache: dict[str, QuestionTemplate] | None = None

    def _load_yaml_file(self, file_path: Path) -> dict:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return yaml.safe_load(file)
        except Exception as e:
            raise RuntimeError(f"Failed to load YAML file {file_path}: {e}") from e

    def _parse_template(self, data: dict, filename: str) -> QuestionTemplate:
        try:
            category_name = data.get("category")
            if not category_name:
                raise ValueError("Missing 'category' field")

            category_info = get_category_by_name(category_name)
            if not category_info:
                raise ValueError(f"Unknown category: {category_name}")

            questions = data.get("questions", [])
            if not questions:
                raise ValueError("Missing 'questions' field")

            return QuestionTemplate(
                category_id=category_info.id,
                category_name=category_info.name,
                questions=questions,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to parse template from {filename}: {e}") from e

    def load_templates(self) -> list[QuestionTemplate]:
        if not self.config_dir.exists():
            raise RuntimeError(f"Configuration directory not found: {self.config_dir}")

        templates = []

        yaml_files = list(self.config_dir.glob("*.yaml")) + list(
            self.config_dir.glob("*.yml")
        )
        if not yaml_files:
            raise RuntimeError(f"No YAML files found in {self.config_dir}")

        for yaml_file in yaml_files:
            try:
                data = self._load_yaml_file(yaml_file)
                template = self._parse_template(data, yaml_file.name)
                templates.append(template)
            except Exception as e:
                print(f"Warning: Skipping {yaml_file.name} due to error: {e}")

        return templates

    def get_templates(self) -> list[QuestionTemplate]:
        if self._templates_cache is None:
            templates = self.load_templates()
            self._templates_cache = {
                f"{t.category_id}_{i}": t for i, t in enumerate(templates)
            }

        return list(self._templates_cache.values())


_loader = YamlTemplateLoader()


def get_yaml_loader() -> YamlTemplateLoader:
    return _loader


def load_default_labels() -> list[str]:
    current_dir = Path(__file__).parent.parent
    config_file = current_dir / "config" / "default_labels.yaml"

    try:
        with open(config_file, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
            return data.get("profile_labels", [])
    except Exception:
        return [
            "自己紹介",
            "趣味・今ハマっていること",
            "好きなコンテンツ",
            "好きな食べ物",
            "得意なこと・特技",
            "実は〇〇なんです",
            "子供の頃の夢",
            "座右の銘",
            "もし１つだけ願いが叶うなら？",
        ]
