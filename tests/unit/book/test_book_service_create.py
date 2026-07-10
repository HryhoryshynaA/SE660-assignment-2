import uuid
import pytest
from application.book.book_service import BookService, _books_db
from tests.builders.book_builder import BookBuilder

class _AuthorServiceStub:
    def __init__(self, exists=True):
        self._exists = exists

    def does_author_exists(self, author_id):
        return self._exists


class TestBookServiceCreateBook:

    def setup_method(self):
        self.service = BookService()
        self.author = _AuthorServiceStub(exists=True)


    def test_create_book_success(self):
        payload = BookBuilder().with_title('Clean Code').as_payload()

        result, errors = self.service.create_book(payload, self.author)

        assert errors is None
        assert result is not None
        assert result.title == 'Clean Code'
        assert result.status == 'UNREAD'
        assert isinstance(result.id, uuid.UUID)
        assert str(result.id) in _books_db

    def test_create_book_with_invalid_data_returns_errors_and_does_not_store(self):
        payload = BookBuilder().with_genre('NOT_A_GENRE').as_payload()
        before_count = len(_books_db)

        result, errors = self.service.create_book(payload, self.author)

        assert result is None
        assert errors is not None
        assert len(_books_db) == before_count

    def test_create_book_rejects_when_author_does_not_exist(self):
        missing_author = _AuthorServiceStub(exists=False)
        payload = BookBuilder().as_payload()

        result, errors = self.service.create_book(payload, missing_author)

        assert result is None
        assert any('not exist' in e for e in errors)

    def test_compute_status_returns_unread_when_pages_read_is_zero(self):
        book = BookBuilder().with_pages_read(0).with_total_pages(100).build_entity()
        assert self.service._compute_status(book) == 'UNREAD'

    def test_compute_status_returns_finished_when_pages_read_equals_total(self):
        book = BookBuilder().with_pages_read(100).with_total_pages(100).build_entity()
        assert self.service._compute_status(book) == 'FINISHED'

    def test_compute_status_returns_in_progress_between_zero_and_total(self):
        book = BookBuilder().with_pages_read(42).with_total_pages(100).build_entity()
        assert self.service._compute_status(book) == 'IN_PROGRESS'