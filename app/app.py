from fastapi import FastAPI, HTTPException
from app.schema import Book, BookUpdate, ErrorResponse

app = FastAPI(
    title="Book Store API",
    description="A simple API for managing books in a store",
    version="1.0.0"
)

# Initialize with sample seed data
books = {
    1: Book(
        id=1,
        title="The Great Gatsby",
        author="F. Scott Fitzgerald",
        price=12.99,
        description="A classic American novel about the Jazz Age",
        isbn="978-0-7432-7356-5",
        publication_year=1925
    ),
    2: Book(
        id=2,
        title="To Kill a Mockingbird",
        author="Harper Lee",
        price=14.99,
        description="A gripping tale of racial injustice and childhood innocence",
        isbn="978-0-06-112008-4",
        publication_year=1960
    ),
    3: Book(
        id=3,
        title="1984",
        author="George Orwell",
        price=13.50,
        description="A dystopian social science fiction novel",
        isbn="978-0-452-28423-4",
        publication_year=1949
    )
}

#gets all books
@app.get("/books", 
         response_model=dict,
         description="Retrieve all books from the store. Use the 'limit' parameter to restrict the number of results.")
def get_all_books(limit: int = None):
    """
    Get all books from the store.
    
    - **limit**: Optional parameter to limit the number of books returned
    - Returns a dictionary of all books (or limited subset if limit is specified)
    """
    if limit and limit > 0:
        return {book.id: book for book in list(books.values())[:limit]}
    return {book.id: book for book in books.values()}

#gets books at a store by ID
@app.get("/books/{book_id}", 
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
         })
def get_book(book_id: int):
    if book_id not in books:
        available_ids = list(books.keys()) if books else []
        suggestion = f"Available book IDs: {available_ids}" if available_ids else "No books available. Create a book first using POST /books"
        raise HTTPException(
            status_code=404,
            detail={
                "error": "BookNotFound",
                "message": f"Book with ID {book_id} was not found in the database.",
                "suggestion": suggestion
            }
        )
    return books.get(book_id)

#creates a new book
@app.post("/books", 
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
          })
def create_book(book: Book):
    if book.id in books:
        existing_book = books[book.id]
        raise HTTPException(
            status_code=400,
            detail={
                "error": "BookAlreadyExists",
                "message": f"Book with ID {book.id} already exists in the database.",
                "suggestion": f"The existing book is: '{existing_book.title}' by {existing_book.author}. Use a different ID or update the existing book using PUT /books/{book.id} endpoint."
            }
        )
    books[book.id] = book
    return book

#updates an existing book (partial update)
@app.put("/books/{book_id}",
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
           })
def update_book(book_id: int, book_update: BookUpdate):
    """
    Update an existing book with partial data.
    
    - **book_id**: The ID of the book to update (from URL path)
    - **book_update**: Partial book data (only include fields you want to update)
    - Returns the updated book
    """
    if book_id not in books:
        available_ids = list(books.keys()) if books else []
        suggestion = f"Available book IDs: {available_ids}" if available_ids else "No books available. Create a book first using POST /books"
        raise HTTPException(
            status_code=404,
            detail={
                "error": "BookNotFound",
                "message": f"Book with ID {book_id} was not found in the database.",
                "suggestion": suggestion
            }
        )
    
    # Get the existing book
    existing_book = books[book_id]
    
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
    
    # Create updated book by merging existing data with update data
    updated_book_data = existing_book.model_dump()
    updated_book_data.update(update_data)
    
    # Create new Book instance with updated data
    updated_book = Book(**updated_book_data)
    
    # Update the book in the dictionary
    books[book_id] = updated_book
    
    return updated_book


@app.delete("/books/{book_id}", response_model=dict, responses={
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
})
def delete_book(book_id: int):
    if book_id not in books:
        available_ids = list(books.keys()) if books else []
        suggestion = f"Available book IDs: {available_ids}" if available_ids else "No books available. Create a book first using POST /books"
        raise HTTPException(
            status_code=404,
            detail={
                "error": "BookNotFound",
                "message": f"Book with ID {book_id} was not found in the database.",
                "suggestion": suggestion,
            },
        )

    # Delete the book from the in-memory "database"
    deleted_book = books.pop(book_id)

    # Return a confirmation response
    return {
        "message": f"Book with ID {book_id} has been deleted successfully.",
        "deleted_book": deleted_book,
    }