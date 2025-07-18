"""
Question template management for the Q&A system.
This module provides structured management of question templates.
"""

from dataclasses import dataclass
from typing import List

from src.db.tables import QuestionCategoryEnum


@dataclass
class QuestionTemplate:
    """A template for creating a group of questions."""

    category: QuestionCategoryEnum
    title: str
    questions: List[str]
    description: str = ""
    is_default: bool = False


# Default question templates
DEFAULT_TEMPLATES = [
    QuestionTemplate(
        category=QuestionCategoryEnum.self_introduction,
        title="自己紹介のための20の質問",
        description="基本的な自己紹介に使える質問集",
        is_default=True,
        questions=[
            "あなたの名前は何ですか？",
            "出身地はどこですか？",
            "趣味は何ですか？",
            "好きな食べ物は何ですか？",
            "好きな映画やドラマはありますか？",
            "休日はどのように過ごしていますか？",
            "最近ハマっていることはありますか？",
            "得意なことは何ですか？",
            "苦手なことはありますか？",
            "将来の夢や目標はありますか？",
            "学生時代の思い出は何ですか？",
            "好きな音楽やアーティストはいますか？",
            "ペットを飼っていますか？",
            "好きな季節はいつですか？",
            "好きな場所はどこですか？",
            "チャームポイントは何ですか？",
            "一番印象に残っている出来事は何ですか？",
            "好きな本はありますか？",
            "マイブームは何ですか？",
            "今やってみたいことは何ですか？",
        ],
    ),
    QuestionTemplate(
        category=QuestionCategoryEnum.values,
        title="価値観を知る30の質問",
        description="価値観や考え方を深く知るための質問集",
        is_default=True,
        questions=[
            "人生で一番大切にしていることは何ですか？",
            "友人関係で重要だと思うことは何ですか？",
            "仕事で大切にしていることは何ですか？",
            "幸せを感じる瞬間はどんな時ですか？",
            "ストレス発散方法は何ですか？",
            "尊敬する人物はいますか？",
            "今一番やりたいことは何ですか？",
            "もし宝くじが当たったら何をしますか？",
            "人生で後悔していることはありますか？",
            "座右の銘や好きな言葉はありますか？",
            "理想の休日の過ごし方は？",
            "恋愛で大切にしていることは何ですか？",
            "家族との関係はどうですか？",
            "お金に対する考え方は？",
            "健康のために気をつけていることは？",
            "環境問題について思うことは？",
            "政治について関心はありますか？",
            "宗教や信仰について思うことは？",
            "教育について思うことは？",
            "技術の発展について思うことは？",
            "コミュニケーションで大切なことは？",
            "リーダーシップについて思うことは？",
            "失敗から学んだことは？",
            "成功の定義は何ですか？",
            "時間の使い方で意識していることは？",
            "新しいことに挑戦する時の心構えは？",
            "人との約束で大切にしていることは？",
            "困った時の相談相手は？",
            "自分の性格で好きなところは？",
            "将来への不安や期待は？",
        ],
    ),
]


def get_category_title(category: QuestionCategoryEnum) -> str:
    """Get the display title for a question category."""
    # Find the title from templates first
    for template in DEFAULT_TEMPLATES:
        if template.category == category:
            return template.title

    # Fallback to default titles
    title_map = {
        QuestionCategoryEnum.self_introduction: "自己紹介のための20の質問",
        QuestionCategoryEnum.values: "価値観を知る30の質問",
        QuestionCategoryEnum.otaku: "オタクを語る50の質問",
        QuestionCategoryEnum.misc: "その他",
    }
    return title_map.get(category, "Q&A")


def get_default_templates() -> List[QuestionTemplate]:
    """Get all default question templates."""
    return [template for template in DEFAULT_TEMPLATES if template.is_default]


def get_template_by_category(category: QuestionCategoryEnum) -> QuestionTemplate | None:
    """Get a specific template by category."""
    for template in DEFAULT_TEMPLATES:
        if template.category == category:
            return template
    return None
