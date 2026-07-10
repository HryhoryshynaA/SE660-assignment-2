import pytest
from application.book.book_service import BookService, _books_db
from tests.builders.book_builder import BookBuilder

class _AuthorServiceStub:
    def __init__(self, exists=True):
        self._exists = exists

    def does_author_exists(self, author_id):
        return self._exists


def seed(builder: BookBuilder):
    book = builder.build_entity()
    _books_db[str(book.id)] = book
    return book


class TestBookServiceUpdate:

    def setup_method(self):
        self.service = BookService()
        self.author = _AuthorServiceStub(exists=True)

    def test_update_book_success(self):
        existing = seed(BookBuilder().with_title('Old Title'))
        payload = BookBuilder().with_title('New Title').as_payload()

        result, errors = self.service.update_book(str(existing.id), payload, self.author)

        assert errors is None
        assert result.title == 'New Title'
        assert result.id == existing.id
        assert result.created_at == existing.created_at

    def test_update_book_preserves_pages_read_when_not_provided_in_payload(self):
        existing = seed(BookBuilder().with_pages_read(42).with_total_pages(100))
        payload = BookBuilder().with_total_pages(100).as_payload()
        assert 'pagesRead' not in payload

        result, errors = self.service.update_book(str(existing.id), payload, self.author)

        assert errors is None
        assert result.pages_read == 42

    def test_update_book_preserves_pages_read_when_not_provided_in_payload(self, monkeypatch):
        monkeypatch.setattr(BookService, '_compute_status', staticmethod(lambda book: 'IN_PROGRESS'))
        existing = seed(BookBuilder().with_pages_read(42).with_total_pages(100))
        payload = BookBuilder().with_total_pages(100).as_payload()
        assert 'pagesRead' not in payload

        result, errors = self.service.update_book(str(existing.id), payload, self.author)

        assert errors is None
        assert result.pages_read == 42

    def test_update_book_with_invalid_data_returns_errors_and_does_not_modify_book(self):
        existing = seed(BookBuilder().with_title('Untouched'))
        payload = BookBuilder().with_genre('NOT_A_GENRE').as_payload()

        result, errors = self.service.update_book(str(existing.id), payload, self.author)

        assert result is None
        assert errors is not None
        assert _books_db[str(existing.id)].title == 'Untouched'

    def test_update_book_rejects_when_author_does_not_exist(self):
        existing = seed(BookBuilder().with_title('Some Book'))
        missing_author = _AuthorServiceStub(exists=False)
        payload = BookBuilder().as_payload()

        result, errors = self.service.update_book(str(existing.id), payload, missing_author)

        assert result is None
        assert any('not exist' in e for e in errors)