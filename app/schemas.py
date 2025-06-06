from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator, EmailStr
from typing import List, Optional


class UserBase(BaseModel):
    id: Optional[int]
    email: Optional[str]
    is_admin: Optional[bool] = False
    books: Optional[List["BooksOut"]]

    class Config:
        orm_model = True
        arbitrary_types_allowed = True


class UserBooks(BaseModel):
    id: int
    email: str

    class Config:
        orm_model = True
        arbitrary_types_allowed = True


class UserIn(BaseModel):
    email: EmailStr
    password: str

    class Config:
        orm_model = True
        arbitrary_types_allowed = True


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
    year_of_public: int
    ISBN: int
    quantity: int
    reader_id: "UserBase"

    class Config:
        orm_model = True
        arbitrary_types_allowed = True


class GetBooks(BaseModel):
    id: int

    class Config:
        orm_model = True
        arbitrary_types_allowed = True


class ReturnBook(BaseModel):
    book_id: int
    borrow_id: int
