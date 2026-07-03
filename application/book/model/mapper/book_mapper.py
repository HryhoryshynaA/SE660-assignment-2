import uuid
from datetime import datetime, timezone
from application.book.model.dto.book import Book

class BookMapper:

    def map_request(self, request_data) -> Book:
        now = datetime.now(timezone.utc).isoformat()
        return Book(
            id = request_data.get('id') or uuid.uuid4(),
            user_id = uuid.UUID(str(request_data.get('userId'))) if request_data.get('userId') else None,
            author_id = uuid.UUID(str(request_data.get('authorId'))) if request_data.get('authorId') else None,
            series_id = uuid.UUID(str(request_data.get('seriesId'))) if request_data.get('seriesId') else None,
            volume_number = request_data.get('volumeNumber'),
            title = request_data.get('title'),
            genre = request_data.get('genre'),
            published_year = request_data.get('publishedYear'),
            total_pages = request_data.get('totalPages'),
            pages_read = request_data.get('pagesRead') or 0,
            status = 'UNREAD',
            created_at = now,
            updated_at = now,
        )

    def map_entity_to_dto(self, entity) -> Book:
        return Book(
            id = entity.id,
            user_id = entity.user_id,
            author_id = entity.author_id,
            series_id = entity.series_id,
            volume_number = entity.volume_number,
            title = entity.title,
            genre = entity.genre,
            published_year = entity.published_year,
            total_pages = entity.total_pages,
            pages_read = entity.pages_read,
            status = entity.status,
            created_at = entity.created_at,
            updated_at = entity.updated_at,
        )

    def map_to_dict(self, book: Book) -> dict:
        return {
            'id': str(book.id),
            'userId': str(book.user_id) if book.user_id else None,
            'authorId': str(book.author_id) if book.author_id else None,
            'seriesId': str(book.series_id) if book.series_id else None,
            'volumeNumber': book.volume_number,
            'title': book.title,
            'genre': book.genre,
            'publishedYear': book.published_year,
            'totalPages': book.total_pages,
            'pagesRead': book.pages_read,
            'status': book.status,
            'createdAt': book.created_at,
            'updatedAt': book.updated_at,
        }