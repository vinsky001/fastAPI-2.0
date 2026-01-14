from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, date

# Error response schema
class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Detailed error message")
    suggestion: Optional[str] = Field(None, description="Helpful suggestion to resolve the error")

# User schemas
class UserCreate(BaseModel):
    """Schema for user registration (creating a new account)."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password (minimum 8 characters)")
    first_name: str = Field(..., min_length=1, max_length=100, description="User's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="User's last name")
    date_of_birth: date = Field(..., description="User's date of birth (YYYY-MM-DD)")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": "1990-05-15"
            }
        }
    }

class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }
    }

class UserResponse(BaseModel):
    """Schema for user API responses (excludes password for security)."""
    id: int = Field(..., description="Unique identifier for the user")
    email: EmailStr = Field(..., description="User's email address")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    date_of_birth: date = Field(..., description="User's date of birth")
    is_active: bool = Field(..., description="Whether the user account is active")
    is_superuser: bool = Field(..., description="Whether the user has superuser privileges")
    created_at: datetime = Field(..., description="Timestamp when the user was created")
    
    model_config = {
        "from_attributes": True,  # allow creating from ORM objects
        "json_schema_extra": {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": "1990-05-15",
                "is_active": True,
                "is_superuser": False,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }
    }

#book schema
class Book(BaseModel):
    id: int = Field(..., description="Unique identifier for the book")
    title: str = Field(..., min_length=1, description="Title of the book")
    author: str = Field(..., min_length=1, description="Author of the book")
    price: float = Field(..., gt=0, description="Price of the book")
    description: Optional[str] = Field(None, description="Description of the book")
    isbn: Optional[str] = Field(None, description="ISBN number of the book")
    publication_year: Optional[int] = Field(None, ge=1000, le=9999, description="Year of publication")
    
    #example of how the book should be formatted in the JSON response
    model_config = {
        "from_attributes": True,  # allow creating from ORM objects
        "json_schema_extra": {
            "example": {
                "id": 1,
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "price": 12.99,
                "description": "A classic American novel",
                "isbn": "978-0-7432-7356-5",
                "publication_year": 1925,
            }
        },
    }

# Book update schema for PUT (all fields optional)
class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, description="Title of the book")
    author: Optional[str] = Field(None, min_length=1, description="Author of the book")
    price: Optional[float] = Field(None, gt=0, description="Price of the book")
    description: Optional[str] = Field(None, description="Description of the book")
    isbn: Optional[str] = Field(None, description="ISBN number of the book")
    publication_year: Optional[int] = Field(None, ge=1000, le=9999, description="Year of publication")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Updated Book Title",
                "price": 15.99,
                "description": "Updated description"
            }
        }
    }