from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schema import Book, BookUpdate, ErrorResponse, UserCreate, UserLogin, UserResponse, Token
from app.db import BookModel, get_session, init_db
from app.users import register_user, login_user, get_current_active_user
from app.db import UserModel

app = FastAPI(
    title="Book Store API",
    description="A simple API for managing books in a store",
    version="1.0.0",
)


@app.on_event("startup")
async def on_startup() -> None:
    # Create database tables on startup
    await init_db()


#gets all books
@app.get(
    "/books",
    response_model=list[Book],
    description="Retrieve all books from the store. Use the 'limit' parameter to restrict the number of results.",
)
async def get_all_books(
    page: int = 1, page_size: int = 20, session: AsyncSession = Depends(get_session)
 ):
    """
    Implemented pagination for retrieving books.
    """
    offset = (page - 1) * page_size
    query = (
        select(BookModel)
        .offset(offset)
        .limit(page_size)
    )
    result = await session.execute(query)
    books = result.scalars().all()
    return [Book.model_validate(book) for book in books]

#gets books at a store by ID
@app.get(
    "/books/{book_id}",
    response_model=Book,
    responses={
             404: {
                 "model": ErrorResponse,
                 "description": "Book not found",
                 "content": {
                     "application/json": {
                         "example": {
                             "error": "BookNotFound",
                             "message": "Book with ID 5 was not found in the database.",
                             "suggestion": "Please check the book ID and try again. You can view all available books using GET /books endpoint."
                         }
                     }
                 }
             }
         },
)
async def get_book(
    book_id: int, session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(BookModel).where(BookModel.id == book_id)
    )
    book = result.scalars().first()

    if book is None:
        # Get available IDs for helpful suggestion
        result_all = await session.execute(select(BookModel.id))
        available_ids = [row[0] for row in result_all.fetchall()]
        suggestion = (
            f"Available book IDs: {available_ids}"
            if available_ids
            else "No books available. Create a book first using POST /books"
        )
        raise HTTPException(
            status_code=404,
            detail={
                "error": "BookNotFound",
                "message": f"Book with ID {book_id} was not found in the database.",
                "suggestion": suggestion,
            },
        )

    return Book.model_validate(book)

#creates a new book
@app.post(
    "/books",
    response_model=Book,
    status_code=201,
    responses={
              400: {
                  "model": ErrorResponse,
                  "description": "Bad request - Book already exists",
                  "content": {
                      "application/json": {
                          "example": {
                              "error": "BookAlreadyExists",
                              "message": "A book with this ID already exists in the database.",
                              "suggestion": "Use a different ID or update the existing book. You can view all books using GET /books endpoint."
                          }
                      }
                  }
              }
          },
)
async def create_book(
    book: Book, session: AsyncSession = Depends(get_session)
):
    # Check if a book with this ID already exists
    result = await session.execute(
        select(BookModel).where(BookModel.id == book.id)
    )
    existing_book = result.scalars().first()

    if existing_book is not None:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "BookAlreadyExists",
                "message": f"Book with ID {book.id} already exists in the database.",
                "suggestion": (
                    f"The existing book is: '{existing_book.title}' by "
                    f"{existing_book.author}. Use a different ID or update "
                    f"the existing book using PUT /books/{book.id} endpoint."
                ),
            },
        )

    db_book = BookModel(**book.model_dump())
    session.add(db_book)
    await session.commit()
    await session.refresh(db_book)

    return Book.model_validate(db_book)

#updates an existing book (partial update)
@app.put(
    "/books/{book_id}",
    response_model=Book,
    responses={
               404: {
                   "model": ErrorResponse,
                   "description": "Book not found",
                   "content": {
                       "application/json": {
                           "example": {
                               "error": "BookNotFound",
                               "message": "Book with ID 5 was not found in the database.",
                               "suggestion": "Please check the book ID and try again. You can view all available books using GET /books endpoint."
                           }
                       }
                   }
               },
               400: {
                   "model": ErrorResponse,
                   "description": "Bad request - Validation error",
                   "content": {
                       "application/json": {
                           "example": {
                               "error": "ValidationError",
                               "message": "Invalid data provided for update.",
                               "suggestion": "Please check the field values and ensure they meet the validation requirements."
                           }
                       }
                   }
              }
           },
)
async def update_book(
    book_id: int,
    book_update: BookUpdate,
    session: AsyncSession = Depends(get_session),
):
    """
    Update an existing book with partial data.
    
    - **book_id**: The ID of the book to update (from URL path)
    - **book_update**: Partial book data (only include fields you want to update)
    - Returns the updated book
    """
    result = await session.execute(
        select(BookModel).where(BookModel.id == book_id)
    )
    existing_book = result.scalars().first()

    if existing_book is None:
        # Build helpful suggestion
        result_all = await session.execute(select(BookModel.id))
        available_ids = [row[0] for row in result_all.fetchall()]
        suggestion = (
            f"Available book IDs: {available_ids}"
            if available_ids
            else "No books available. Create a book first using POST /books"
        )
        raise HTTPException(
            status_code=404,
            detail={
                "error": "BookNotFound",
                "message": f"Book with ID {book_id} was not found in the database.",
                "suggestion": suggestion,
            },
        )
    
    # Convert to dict, exclude None values (fields not being updated)
    update_data = book_update.model_dump(exclude_unset=True)
    
    # Check if at least one field is being updated
    if not update_data:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "NoUpdateData",
                "message": "No fields provided for update.",
                "suggestion": "Please provide at least one field to update (title, author, price, description, isbn, or publication_year)."
            }
        )
    
    # Apply updates to the ORM object
    for field, value in update_data.items():
        setattr(existing_book, field, value)

    await session.commit()
    await session.refresh(existing_book)

    return Book.model_validate(existing_book)


@app.delete(
    "/books/{book_id}",
    response_model=dict,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Book not found",
            "content": {
                "application/json": {
                    "example": {
                        "error": "BookNotFound",
                        "message": "Book with ID 5 was not found in the database.",
                        "suggestion": "Please check the book ID and try again. You can view all available books using GET /books endpoint.",
                    }
                }
            },
        }
    },
)
async def delete_book(
    book_id: int, session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(BookModel).where(BookModel.id == book_id)
    )
    existing_book = result.scalars().first()

    if existing_book is None:
        # Build helpful suggestion
        result_all = await session.execute(select(BookModel.id))
        available_ids = [row[0] for row in result_all.fetchall()]
        suggestion = (
            f"Available book IDs: {available_ids}"
            if available_ids
            else "No books available. Create a book first using POST /books"
        )
        raise HTTPException(
            status_code=404,
            detail={
                "error": "BookNotFound",
                "message": f"Book with ID {book_id} was not found in the database.",
                "suggestion": suggestion,
            },
        )

    # Delete the book from the database
    await session.delete(existing_book)
    await session.commit()

    deleted_book = Book.model_validate(existing_book)

    # Return a confirmation response
    return {
        "message": f"Book with ID {book_id} has been deleted successfully.",
        "deleted_book": deleted_book,
    }


# ==================== USER AUTHENTICATION ROUTES ====================

@app.post("/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserCreate):
    """
    Register a new user account.
    
    Creates a new user with the provided information and returns the user details.
    """
    return await register_user(user_data)


@app.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """
    Login a user and receive a JWT access token.
    
    Returns a JWT token that expires in 30 minutes. Use this token in the Authorization header
    for protected endpoints: `Authorization: Bearer <token>`
    """
    return await login_user(user_credentials)


@app.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserModel = Depends(get_current_active_user)):
    """
    Get the current authenticated user's information.
    
    Requires a valid JWT token in the Authorization header.
    """
    return UserResponse.model_validate(current_user)