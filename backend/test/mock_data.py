from datetime import datetime
from uuid import uuid4

USERS: list = []

TEMPLATES = [
    {
        "id": "basic-10",
        "title": "基本テンプレート",
        "description": None,
        "created_at": datetime(2024, 1, 1, 12, 0, 0),
    },
]

QUESTIONS = [
    {
        "id": uuid4(),
        "template_id": "basic-10",
        "order": 1,
        "text": "好きな食べ物は？",
        "created_at": datetime(2024, 1, 1, 12, 1, 0),
    },
    {
        "id": uuid4(),
        "template_id": "basic-10",
        "order": 2,
        "text": "趣味は？",
        "created_at": datetime(2024, 1, 1, 12, 2, 0),
    },
]

ANSWERS: list = []
