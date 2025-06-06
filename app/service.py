from models import *

MAX_BOOKS = 3

def check_book(user: Users, book_id: Books):
    user_books = user.books
    if len(user_books) >= MAX_BOOKS:
        return False
    for book in user_books:
        if book.id == book_id:
            return False
    return True