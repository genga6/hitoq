from humps import camelize
from pydantic import BaseModel


def to_camel(string: str) -> str:
    # snake_case -> camel_case
    return camelize(string)


class OrmBaseModel(BaseModel):
    class Config:
        from_attributes = True
        alias_generator = to_camel
        populate_by_name = True
