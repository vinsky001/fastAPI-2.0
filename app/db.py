from collections.abc import AsyncGenerator

from sqlalchemy import Boolean, Column, Date, DateTime, Float, Integer, String, Text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func


# SQLite database URL (async)
DATABASE_URL = "sqlite+aiosqlite:///./test.db"


class Base(DeclarativeBase):
    """Base class for all ORM models."""

#
class UserModel(Base):
    """SQLAlchemy ORM model for the users table (accounts)."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    is_active = Column(Boolean, nullable=False, server_default="1")
    is_superuser = Column(Boolean, nullable=False, server_default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class BookModel(Base):
    """SQLAlchemy ORM model for the books table."""

    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    isbn = Column(String(50), nullable=True, unique=True)
    publication_year = Column(Integer, nullable=True)


# Async engine and session factory
engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides an async SQLAlchemy session."""
    async with async_session_maker() as session:
        yield session


async def init_db() -> None:
    """Initialize the database (create tables)."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

        