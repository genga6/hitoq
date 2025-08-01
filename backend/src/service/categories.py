from dataclasses import dataclass


@dataclass
class CategoryInfo:
    id: str
    name: str
    description: str


CATEGORIES = [
    CategoryInfo(
        id="values", name="価値観", description="人生観、考え方、大切にしていること"
    ),
    CategoryInfo(
        id="personality",
        name="性格・特徴",
        description="自分の性格、特徴、個性について",
    ),
    CategoryInfo(
        id="relationships",
        name="人間関係",
        description="友人、家族、コミュニケーションについて",
    ),
    CategoryInfo(
        id="romance", name="恋愛", description="恋愛観、パートナーシップについて"
    ),
    CategoryInfo(
        id="childhood", name="子供時代", description="幼少期の思い出、体験、遊び"
    ),
    CategoryInfo(
        id="school", name="学生時代", description="学校生活、青春の思い出、勉強"
    ),
    CategoryInfo(
        id="career", name="キャリア", description="仕事、働き方、キャリアプラン"
    ),
    CategoryInfo(
        id="lifestyle",
        name="ライフスタイル",
        description="日常の過ごし方、健康、ファッション、インテリア",
    ),
    CategoryInfo(
        id="activities",
        name="アクティビティ",
        description="旅行、グルメ、アウトドア活動",
    ),
    CategoryInfo(
        id="entertainment",
        name="エンタメ",
        description="映画、音楽、ゲーム、読書、創作、趣味",
    ),
    CategoryInfo(id="goals", name="目標", description="学習、成長、将来の目標、夢"),
    CategoryInfo(
        id="hypothetical",
        name="もしも",
        description="仮定の質問、想像の世界、「もし～だったら」",
    ),
]


def get_category_by_id(category_id: str) -> CategoryInfo | None:
    for category in CATEGORIES:
        if category.id == category_id:
            return category
    return None


def get_category_by_name(category_name: str) -> CategoryInfo | None:
    for category in CATEGORIES:
        if category.name == category_name:
            return category
    return None


def get_all_categories() -> list[CategoryInfo]:
    return CATEGORIES.copy()


def get_categories_dict() -> dict[str, CategoryInfo]:
    return {category.id: category for category in CATEGORIES}


def get_category_names_dict() -> dict[str, str]:
    return {category.id: category.name for category in CATEGORIES}


def is_valid_category_id(category_id: str) -> bool:
    return any(category.id == category_id for category in CATEGORIES)


def is_valid_category_name(category_name: str) -> bool:
    return any(category.name == category_name for category in CATEGORIES)
