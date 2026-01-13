from fastapi import FastAPI, HTTPException

app = FastAPI()

books = {}

#gets all books
@app.get("/books")
def get_all_books(limit: int):
    if limit:
        return list(books.values())[:limit]
    return books

#gets books at a store by ID
@app.get("/books/{book_id}")
def get_book(book_id: int):
    if not book_id in books:
        raise HTTPException(status_code=404, detail="Book not found")
    return books.get(book_id)

@app.post("/books")
def create_book(book: str, book_id: int):
    pass