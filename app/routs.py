import datetime

import models
from service import check_book
from datetime import timedelta, datetime
from typing import Annotated, List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import select, update, or_, delete
from starlette.responses import JSONResponse

from schemas import UserBase, UserIn, BooksOut, GetBooks, ReturnBook
from auth import (Token, authenticate_user,
                  create_access_token,
                  get_current_active_user,
                  ACCESS_TOKEN_EXPIRE_MINUTES,
                  get_password_hash, )
from database import engine, session

app = FastAPI()


# @app.on_event("startup")
# async def startup():
#     async with engine.begin() as conn:
#         await conn.run_sync(models.Base.metadata.create_all)

async def connection():
    async with session as conn:
        yield conn


# async def shutdown():
#     await session.close()
#     await engine.dispose()


@app.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    print(form_data.username, form_data.password)
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.post('/registration', response_model=UserBase)
async def registrations(
        credentials: UserIn,
        conn=Depends(connection)

):
    password = get_password_hash(credentials.password)
    new_user = models.Users(email=credentials.email, password=password, books=[])
    try:
        conn.add(new_user)
        await conn.commit()
        return new_user
    except:
        await session.rollback()
        return JSONResponse({"error": "this email already used"})


@app.get("/users/me/", response_model=UserBase)
async def read_users_me(
        current_user: Annotated[models.Users, Depends(get_current_active_user)],
):
    return current_user


@app.get("/users", response_model=List[UserBase])
async def get_all_users():
    query = select(models.Users)
    result = await session.execute(query)
    users = result.scalars().all()
    return users


@app.get('/books', response_model=List[BooksOut])
async def get_books():
    query = select(models.Books).where(models.Books.quantity > 0)
    result = await session.execute(query)
    books = result.scalars().unique().all()
    return books


@app.post('/books/get', response_model=BooksOut)
async def book_issue(
        book_id: GetBooks,
        user: Annotated[models.Users, Depends(get_current_active_user)],
        conn=Depends(connection)
):
    query = select(models.Books).where(models.Books.id == book_id.id)
    result = await conn.execute(query)
    book = result.scalars().unique().one_or_none()
    possibility_check = check_book(user, book_id.id)
    if book and book.quantity > 0:
        if possibility_check:
            quantity = book.decrement_quantity
            update_value = update(models.Books).where(models.Books.id == book_id.id).values(quantity=quantity)
            borrowed_books = models.BorrowedBooks(book_id=book_id.id, reader_id=user.id)
            associate = models.AssociateTable(reader_id=user.id, book_id=book_id.id)
            await conn.execute(update_value)
            conn.add_all([borrowed_books, associate])
            await conn.commit()
            return book
        else:
            return JSONResponse({"message": "You already have this book"})
    return JSONResponse({"err": "This book is finished"})


@app.post("/books/return")
async def return_book(
        book: ReturnBook,
        user: Annotated[models.Users, Depends(get_current_active_user)],
        conn=Depends(connection)
):
    query = select(models.BorrowedBooks).where(or_(
        models.BorrowedBooks.book_id == book.book_id, models.BorrowedBooks.id == book.borrow_id)).where(
        models.BorrowedBooks.reader_id == user.id, models.BorrowedBooks.return_date == None)
    result = await conn.execute(query)
    borrowed_book = result.scalars().one_or_none()
    if borrowed_book and borrowed_book.return_date is None:
        borrowed_book.return_date = datetime.utcnow()
        stmt = select(models.Books).where(models.Books.id == borrowed_book.book_id)
        res = await conn.execute(stmt)
        getted_book = res.scalars().unique().one_or_none()
        update_book = update(models.Books).where(models.Books.id == book.book_id).values(
            quantity=getted_book.increment_quantity)
        del_associate = delete(models.AssociateTable).where(models.AssociateTable.reader_id == user.id,
                                                            models.AssociateTable.book_id == book.book_id)
        await conn.execute(del_associate)
        await conn.execute(update_book)
        await conn.commit()
        return borrowed_book
    return JSONResponse({"message": "This book already return"})
