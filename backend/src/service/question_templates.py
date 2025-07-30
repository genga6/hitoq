from dataclasses import dataclass
from typing import List

from src.db.tables import QuestionCategoryEnum
from src.service.yaml_loader import QuestionTemplate, get_yaml_loader


@dataclass
class CategoryInfo:
    id: str
    label: str
    description: str = ""


CATEGORY_INFO = {
    QuestionCategoryEnum.self_introduction: CategoryInfo(
        id="self-introduction",
        label="自己紹介",
        description="基本的な自己紹介に関する質問",
    ),
    QuestionCategoryEnum.values: CategoryInfo(
        id="values", label="価値観", description="価値観や考え方に関する質問"
    ),
    QuestionCategoryEnum.otaku: CategoryInfo(
        id="otaku", label="趣味・創作", description="趣味や創作活動に関する質問"
    ),
    QuestionCategoryEnum.misc: CategoryInfo(
        id="misc",
        label="ライフスタイル",
        description="日常生活やライフスタイルに関する質問",
    ),
}


def get_category_title(category: QuestionCategoryEnum) -> str:
    loader = get_yaml_loader()
    template = loader.get_template_by_category(category)
    if template:
        return template.title

    title_map = {
        QuestionCategoryEnum.self_introduction: "自己紹介のための30の質問",
        QuestionCategoryEnum.values: "価値観を知る40の質問",
        QuestionCategoryEnum.otaku: "趣味を語る50の質問",
        QuestionCategoryEnum.misc: "ライフスタイル診断30の質問",
    }
    return title_map.get(category, "Q&A")


def get_default_templates() -> List[QuestionTemplate]:
    loader = get_yaml_loader()
    return loader.get_templates()


def get_template_by_category(category: QuestionCategoryEnum) -> QuestionTemplate | None:
    loader = get_yaml_loader()
    return loader.get_template_by_category(category)


def get_category_info(category: QuestionCategoryEnum) -> CategoryInfo:
    return CATEGORY_INFO[category]


def get_all_category_info() -> dict[str, CategoryInfo]:
    return {info.id: info for info in CATEGORY_INFO.values()}
