from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import asyncio
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = 'postgresql+asyncpg://admin:qwertyu123@localhost:5433/libraryAPI'

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

async_session = sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)
session = async_session()
# Base = declarative_base()

# class SessionContextManager:
#
#     def __init__(self) -> None:
#         self.session_factory = async_session
#         self.session = None
#
#     def __enter__(self) -> None:
#         self.session = self.session_factory()
#
#     def __exit__(self, *args: object) -> None:
#         self.rollback()
#
#     async def commit(self) -> None:
#         await self.session.commit()
#         await self.session.close()
#         self.session = None
#
#     async def rollback(self) -> None:
#         await self.session.rollback()
#         await self.session.close()
#         self.session = None
#
# session = SessionContextManager()




