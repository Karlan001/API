from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator, EmailStr
from typing import List, Optional

class UserBase(BaseModel):
    # model_config = ConfigDict(arbitrary_types_allowed=True)
    id: Optional[int]
    email: Optional[str] = None
    is_admin: Optional[bool] = False

    class Config:
        orm_model = True
        arbitrary_types_allowed = True

class UserIn(BaseModel):
    email: EmailStr
    password: str


class BooksOut(BaseModel):
    id: int
    title: str
    author: str
    year_of_public: int | None
    ISBN: int | None
    quantity: int
    reader_id: int | None

    class Config:
        orm_model = True
        arbitrary_types_allowed = True


class BooksIn(BaseModel):
    id: int
    title: str
    author: str
    year_of_public: datetime
    ISBN: int
    quantity: int
    reader_id: 'UserBase'

    class Config:
        orm_model = True
        arbitrary_types_allowed = True

