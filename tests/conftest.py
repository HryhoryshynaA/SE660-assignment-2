import pytest

import application.author.author_service as author_service_module
import application.book.book_service as book_service_module
from application import app as flask_app
AUTHOR_CONTRACT = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "firstName": {"type": "string"},
        "lastName": {"type": "string"},
        "nationality": {"type": ["string", "null"]},
        "createdAt": {"type": "string"}
    },
    "required": ["id", "firstName", "lastName", "createdAt"],
    "additionalProperties": False
}

BOOK_CONTRACT = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "userId": {"type": "string"},
        "authorId": {"type": "string"},
        "seriesId": {"type": ["string", "null"]},
        "volumeNumber": {"type": ["integer", "null"]},
        "title": {"type": "string"},
        "genre": {"type": "string"},
        "publishedYear": {"type": "integer"},
        "totalPages": {"type": "integer"},
        "pagesRead": {"type": "integer"},
        "status": {"type": "string", "enum": ["UNREAD", "IN_PROGRESS", "FINISHED"]},
        "createdAt": {"type": "string"},
        "updatedAt": {"type": "string"}
    },
    "required": ["id", "userId", "authorId", "title", "genre", "publishedYear",
                 "totalPages", "pagesRead", "status", "createdAt", "updatedAt"],
    "additionalProperties": False
}


@pytest.fixture(autouse=True)
def reset_in_memory_db():
    author_service_module._authors_db.clear()
    book_service_module._books_db.clear()
    yield
    author_service_module._authors_db.clear()
    book_service_module._books_db.clear()

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as c:
        yield c


@pytest.fixture
def author_service():
    from application.author.author_service import AuthorService
    return AuthorService()


@pytest.fixture
def book_service():
    from application.book.book_service import BookService
    return BookService()


def valid_book_payload(**overrides):
    payload = {
        'userId': '11111111-1111-1111-1111-111111111111',
        'authorId': '22222222-2222-2222-2222-222222222222',
        'title': 'Sample Book',
        'genre': 'FICTION',
        'publishedYear': 2020,
        'totalPages': 200,
    }
    payload.update(overrides)
    return payload


def valid_author_payload(**overrides):
    payload = {
        'firstName': 'Jane',
        'lastName': 'Doe',
        'nationality': 'American',
    }
    payload.update(overrides)
    return payload

