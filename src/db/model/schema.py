from pydantic import BaseModel


class AnswerModel(BaseModel):
    user_id: str
    question_id: int
    text: str
