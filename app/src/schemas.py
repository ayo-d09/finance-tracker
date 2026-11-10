from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class EntryCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    amount: Decimal = Field(gt=0)
    type: Literal["income", "expense"]
    description: str = Field(min_length=1, max_length=500)
    date: date
    

class EntryResponse(BaseModel):
    id: int
    amount: Decimal
    type: Literal["income", "expense"]
    description: str
    date: date
    created_at: datetime
