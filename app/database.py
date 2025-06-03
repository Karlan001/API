from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = 'postgresql+asyncpg://admin:qwertyu123@localhost:5433/libraryAPI'

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

async_session = sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)
session = async_session()
# Base = declarative_base()

# asyncio.run(session.execute(text("""select * from test_table""")))
# asyncio.run(session.info)

# async def main() -> None:
#     async with session as conn:
#         result = await conn.execute(text("""select * from users"""))
#         print(result.fetchone())
# #
# asyncio.run(main())
