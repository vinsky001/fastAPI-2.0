from pydantic import BaseModel, Field
from typing import Optional

# Error response schema
class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Detailed error message")
    suggestion: Optional[str] = Field(None, description="Helpful suggestion to resolve the error")

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
        "json_schema_extra": {
            "example": {
                "id": 1,
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "price": 12.99,
                "description": "A classic American novel",
                "isbn": "978-0-7432-7356-5",
                "publication_year": 1925
            }
        }
    }