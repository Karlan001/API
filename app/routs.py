import models
from service import check_book
from datetime import timedelta
from typing import Annotated, List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import select, update, or_
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


async def shutdown():
    await session.close()
    await engine.dispose()


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
async def registrations(credentials: UserIn):
    password = get_password_hash(credentials.password)
    new_user = models.Users(email=credentials.email, password=password, books=[])
    try:
        session.add(new_user)
        await session.commit()
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
    query = select(models.Users).options(selectinload(models.Users.books))
    result = await session.execute(query)
    users = result.scalars().all()
    return users


@app.get('/books', response_model=List[BooksOut])
async def get_books():
    query = select(models.Books).options(joinedload(models.Books.reader))
    result = await session.execute(query)
    books = result.scalars().all()
    return books


@app.post('/books/get', response_model=BooksOut)
async def book_issue(
        book_id: GetBooks,
        user: Annotated[models.Users, Depends(get_current_active_user)],
):
    query = select(models.Books).where(models.Books.id == book_id.id)
    result = await session.execute(query)
    book = result.scalars().one_or_none()
    possibility_check = check_book(user, book_id.id)
    if book and book.quantity > 0:
        if possibility_check:
            quantity = book.quantity - 1
            update_value = update(models.Books).where(models.Books.id == book_id.id).values(quantity=quantity,
                                                                                            reader_id=user.id)
            borrowed_books = models.BorrowedBooks(book_id=book_id.id, reader_id=user.id)
            await session.execute(update_value)
            session.add(borrowed_books)
            await session.commit()
            return book
        else:
            await session.rollback()
            return JSONResponse({"message": "You already have this book"})
    await session.rollback()
    return JSONResponse({"err": "This book is finished"})


@app.post("/books/return")
async def return_book(
        book: ReturnBook,
        user: Annotated[models.Users, Depends(get_current_active_user)]
):
    query = select(models.BorrowedBooks).where(or_(
        models.BorrowedBooks.book_id == book.book_id, models.BorrowedBooks.id == book.borrow_id))
    result = await session.execute(query)
    borrowed_book = result.scalars().one_or_none()
    return borrowed_book

