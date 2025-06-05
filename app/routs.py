from datetime import timedelta
from typing import Annotated, List

from fastapi import FastAPI, Depends, HTTPException, APIRouter, status

from schemas import UserBase, UserIn, BooksOut
from auth import (Token, authenticate_user,
                  create_access_token,
                  get_current_active_user,
                  ACCESS_TOKEN_EXPIRE_MINUTES,
                  get_password_hash,)
from database import engine, session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select

import models

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


@app.get("/users/me/", response_model=UserBase)
async def read_users_me(
        current_user: Annotated[models.Users, Depends(get_current_active_user)],
):
    return current_user


@app.post('/registration', response_model=UserBase)
async def registrations(new_user: UserIn):
    password = get_password_hash(new_user.password)
    new_user = models.Users(email=new_user.email, password=password)
    session.add(new_user)
    await session.commit()
    return new_user

@app.get('/books', response_model=List[BooksOut])
async def get_books(user: Annotated[models.Users, Depends(get_current_active_user)]):
    query = select(models.Books)
    result = await session.execute(query)
    books = result.scalars().all()
    return books

