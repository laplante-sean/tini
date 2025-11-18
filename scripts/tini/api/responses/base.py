from pydantic import BaseModel, Field
from typing import Any


class BaseResponse(BaseModel):
    typename: Any = Field(alias="__typename")
