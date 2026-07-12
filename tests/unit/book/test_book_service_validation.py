import pytest

from application.book.book_service import BookService
from tests.builders.book_builder import BookBuilder


class _AuthorServiceStub:
    def __init__(self, exists=True):
        self._exists = exists

    def does_author_exists(self, author_id):
        return self._exists


class TestBookServiceValidation:

    def setup_method(self):
        self.service = BookService()
        self.author_exists = _AuthorServiceStub(exists=True)
        self.author_missing = _AuthorServiceStub(exists=False)

    def test_valid_payload_produces_no_errors(self):
        payload = BookBuilder().as_payload()

        errors = self.service._validate(payload, self.author_exists)

        assert errors == []

    def test_missing_title_is_reported(self):
        payload = BookBuilder().without('title').as_payload()

        errors = self.service._validate(payload, self.author_exists)

        assert any('title' in e for e in errors)

    def test_title_over_255_chars_is_rejected(self):
        payload = BookBuilder().with_title('x' * 256).as_payload()

        errors = self.service._validate(payload, self.author_exists)

        assert any('title' in e for e in errors)

    def test_missing_user_id_is_reported(self):
        payload = BookBuilder().without('userId').as_payload()

        errors = self.service._validate(payload, self.author_exists)

        assert any('userId' in e for e in errors)

    def test_nonexistent_author_is_rejected(self):
        payload = BookBuilder().as_payload()

        errors = self.service._validate(payload, self.author_missing)

        assert any('not exist' in e for e in errors)

    def test_missing_author_id_is_reported(self):
        payload = BookBuilder().without('authorId').as_payload()

        errors = self.service._validate(payload, self.author_exists)

        assert any('authorId' in e for e in errors)

    def test_invalid_genre_is_rejected(self):
        payload = BookBuilder().with_genre('NOT_A_REAL_GENRE').as_payload()

        errors = self.service._validate(payload, self.author_exists)

        assert any('genre' in e for e in errors)

    @pytest.mark.parametrize('year', [0, -1, 1449, 3000])
    def test_published_year_outside_valid_range_is_rejected(self, year):
        payload = BookBuilder().with_published_year(year).as_payload()

        errors = self.service._validate(payload, self.author_exists)

        assert any('publishedYear' in e for e in errors)

    def test_non_integer_published_year_is_rejected(self):
        payload = BookBuilder().with_published_year('2020').as_payload()

        errors = self.service._validate(payload, self.author_exists)

        assert any('publishedYear' in e for e in errors)

    @pytest.mark.parametrize('total_pages', [0, -10])
    def test_non_positive_total_pages_is_rejected(self, total_pages):
        payload = BookBuilder().with_total_pages(total_pages).as_payload()

        errors = self.service._validate(payload, self.author_exists)

        assert any('totalPages' in e for e in errors)

    def test_series_id_without_volume_number_is_rejected(self):
        payload = BookBuilder().as_payload()
        payload['seriesId'] = 'series-1'

        errors = self.service._validate(payload, self.author_exists)

        assert any('seriesId and volumeNumber' in e for e in errors)

    def test_volume_number_without_series_id_is_rejected(self):
        payload = BookBuilder().as_payload()
        payload['volumeNumber'] = 2

        errors = self.service._validate(payload, self.author_exists)

        assert any('seriesId and volumeNumber' in e for e in errors)

    def test_series_id_and_volume_number_together_is_valid(self):
        payload = BookBuilder().with_series(series_id='11111111-1111-1111-1111-111111111111',
                                             volume_number=2).as_payload()

        errors = self.service._validate(payload, self.author_exists)

        assert errors == []

    def test_multiple_validation_errors_are_all_reported_together(self):
        payload = BookBuilder().without('title').without('userId').without('authorId') \
            .without('genre').without('publishedYear').without('totalPages').as_payload()
        payload['title'] = ''

        errors = self.service._validate(payload, self.author_missing)
        assert len(errors) >= 5