from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")
DB_PORT = os.environ.get("DB_PORT", "5432")

def get_conn():
    return psycopg2.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASS, dbname=DB_NAME, port=DB_PORT
    )

class Book(BaseModel):
    id: int | None = None
    title: str
    author: str
    pages: int

@app.on_event("startup")
def startup():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS books (
      id SERIAL PRIMARY KEY,
      title TEXT NOT NULL,
      author TEXT NOT NULL,
      pages INT NOT NULL
    )""")
    conn.commit()
    cur.close()
    conn.close()

@app.post("/books", response_model=Book)
def create_book(b: Book):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "INSERT INTO books (title, author, pages) VALUES (%s, %s, %s) RETURNING id, title, author, pages",
        (b.title, b.author, b.pages),
    )
    book = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return book

@app.get("/books")
def list_books():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, title, author, pages FROM books ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, title, author, pages FROM books WHERE id = %s", (book_id,))
    book = cur.fetchone()
    cur.close()
    conn.close()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book