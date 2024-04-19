from datetime import datetime
from pydantic import BaseModel,Field
from pydantic_core import core_schema
from bson import ObjectId
from typing import Any

class RecordId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId')
        return ObjectId(v)

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: Any) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

class Record(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            RecordId: str
        }

    id: RecordId = Field(default_factory=RecordId, alias='_id')
    type: str
    amount: float
    account: str
    category: str
    date: datetime.date
    time: datetime.time