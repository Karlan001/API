from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import ForeignKey
from datetime import datetime
from typing import List, Optional
# from database import Base

class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_admin: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(default=datetime.utcnow())
    books: Mapped[Optional[List['Books']]] = relationship(back_populates='reader')


class Books(Base):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    author: Mapped[str] = mapped_column(nullable=False)
    year_of_public: Mapped[Optional[int]]
    ISBN: Mapped[Optional[int]] = mapped_column(unique=True)
    quantity: Mapped[int] = mapped_column(default=0)
    appended_at: Mapped[Optional[datetime]] = mapped_column(default=datetime.utcnow())
    reader_id: Mapped[Optional['Users']] = mapped_column(ForeignKey('users.id'))
    reader: Mapped[Optional['Users']] = relationship(back_populates='books')

# if __name__ == '__main__':
#     async def startup():
#         async with engine.begin() as conn:
#             await conn.run_sync(Base.metadata.create_all)
#
#     asyncio.run(startup())
