import uuid
from datetime import datetime, timezone
from application.book.model.dto.book import Book

class BookBuilder:
    def __init__(self):
        self._fields = {
            'userId': str(uuid.uuid4()),
            'authorId': str(uuid.uuid4()),
            'title': 'Sample Book',
            'genre': 'FICTION',
            'publishedYear': 2020,
            'totalPages': 200,
        }
        self._status = 'UNREAD'

    def with_title(self, title):
        self._fields['title'] = title
        return self

    def with_genre(self, genre):
        self._fields['genre'] = genre
        return self

    def with_user_id(self, user_id):
        self._fields['userId'] = str(user_id)
        return self

    def with_author_id(self, author_id):
        self._fields['authorId'] = str(author_id)
        return self

    def with_published_year(self, year):
        self._fields['publishedYear'] = year
        return self

    def with_total_pages(self, total_pages):
        self._fields['totalPages'] = total_pages
        return self

    def with_pages_read(self, pages_read):
        self._fields['pagesRead'] = pages_read
        return self

    def with_series(self, series_id, volume_number):
        self._fields['seriesId'] = str(series_id)
        self._fields['volumeNumber'] = volume_number
        return self

    def with_status(self, status):
        self._status = status
        return self

    def without(self, field_name):
        self._fields.pop(field_name, None)
        return self

    def as_payload(self) -> dict:
        return dict(self._fields)

    def build_entity(self) -> Book:
        now = datetime.now(timezone.utc).isoformat()
        return Book(
            id=uuid.uuid4(),
            user_id=uuid.UUID(self._fields['userId']) if self._fields.get('userId') else uuid.uuid4(),
            author_id=uuid.UUID(self._fields['authorId']) if self._fields.get('authorId') else uuid.uuid4(),
            series_id=uuid.UUID(self._fields['seriesId']) if self._fields.get('seriesId') else None,
            volume_number=self._fields.get('volumeNumber'),
            title=self._fields.get('title', 'Sample Book'),
            genre=self._fields.get('genre', 'FICTION'),
            published_year=self._fields.get('publishedYear', 2020),
            total_pages=self._fields.get('totalPages', 200),
            pages_read=self._fields.get('pagesRead', 0),
            status=self._status,
            created_at=now,
            updated_at=now,
        )