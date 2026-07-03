from flask import Flask
from application.author.author_service import AuthorService
from application.book.book_service import BookService


app = Flask(__name__)
author_service  = AuthorService()
book_service = BookService()

import application.author.author_controller
import application.book.book_controller