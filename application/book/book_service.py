from datetime import datetime, timezone
from application.book.model.dto.book import Book, VALID_GENRES
from application.book.model.mapper.book_mapper import BookMapper
import math
from application.models import Page

_books_db: dict[str, Book] = {}

class BookFilters:
    def __init__(self, genre, status, author_id, published_year_from, published_year_to):
        self.genre = genre
        self.status = status
        self.author_id = author_id
        self.published_year_from = published_year_from
        self.published_year_to = published_year_to

class BookService:
    def __init__(self):
        self.book_mapper = BookMapper()

    def _compute_status(self, book: Book) -> str:
        if book.pages_read == 0:
            return 'UNREAD'
        if book.pages_read >= book.total_pages:
            return 'FINISHED'
        return 'IN_PROGRESS'

    def _validate(self, request_data, author_service) -> list[str]:
        errors = []
        title = request_data.get('title', '')
        if not title or not (1 <= len(title) <= 255):
            errors.append('title is must be 1–255 characters')

        if not request_data.get('userId'):
            errors.append('userId is required')

        author_id = request_data.get('authorId')
        if not author_id:
            errors.append('authorId is required')
        elif not author_service.does_author_exists(str(author_id)):
            errors.append(f'authorId {author_id} not exist')

        genre = request_data.get('genre')
        if not genre or genre not in VALID_GENRES:
            errors.append(f'genre must be one of: {", ".join(sorted(VALID_GENRES))}')

        year = request_data.get('publishedYear')
        if year is None:
            errors.append('publishedYear is required')
        elif not isinstance(year, int) or not (1450 <= year <= datetime.now().year):
            errors.append(f'publishedYear must be an integer between 1450 {datetime.now().year}')

        total = request_data.get('totalPages')
        if total is None:
            errors.append('totalPages is required')
        elif not isinstance(total, int) or total <= 0:
            errors.append('totalPages must be a positive integer')

        has_series = bool(request_data.get('seriesId'))
        has_volume = request_data.get('volumeNumber') is not None
        if has_series != has_volume:
            errors.append('seriesId and volumeNumber must be given together or not at all')

        return errors

    def create_book(self, request_data, author_service):
        errors = self._validate(request_data, author_service)
        if errors:
            return None, errors
        book = self.book_mapper.map_request(request_data)
        book.status = self._compute_status(book)
        _books_db[str(book.id)] = book
        return self.book_mapper.map_entity_to_dto(book), None

    def get_book(self, book_id):
        book = _books_db.get(str(book_id))
        if book is None:
            return None
        return self.book_mapper.map_entity_to_dto(book)

    def update_book(self, book_id, request_data, author_service):
        book = _books_db.get(str(book_id))
        if book is None:
            return None, None
        if 'pagesRead' not in request_data:
            request_data['pagesRead'] = book.pages_read
        errors = self._validate(request_data, author_service)
        if errors:
            return None, errors
        request_data['id'] = book.id
        updated = self.book_mapper.map_request(request_data)
        updated.created_at = book.created_at
        updated.updated_at = datetime.now(timezone.utc).isoformat()
        updated.status = self._compute_status(updated)
        _books_db[str(book_id)] = updated
        return self.book_mapper.map_entity_to_dto(updated), None

    def delete_book(self, book_id) -> bool:
        if str(book_id) not in _books_db:
            return False
        del _books_db[str(book_id)]
        return True

    def books_by_author(self, author_id) -> list:
        return [b for b in _books_db.values() if str(b.author_id) == str(author_id)]

    def get_books(self, filters: BookFilters, page, size, sort='title', order='asc') -> Page:
        items = list(_books_db.values())

        if filters.genre:
            items = [b for b in items if b.genre == filters.genre]
        if filters.status:
            items = [b for b in items if b.status == filters.status]
        if filters.author_id:
            items = [b for b in items if str(b.author_id) == str(filters.author_id)]
        if filters.published_year_from is not None:
            items = [b for b in items if b.published_year >= filters.published_year_from]
        if filters.published_year_to is not None:
            items = [b for b in items if b.published_year <= filters.published_year_to]

        attr_map = {'title': 'title', 'publishedYear': 'published_year'}
        key = attr_map.get(sort, 'title')
        items.sort(key=lambda b: getattr(b, key, ''), reverse=(order == 'desc'))

        total_pages = max(1, math.ceil(len(items) / size))
        start = (page - 1) * size

        return Page(
            size=size,
            page=page,
            total_pages=total_pages,
            content=[self.book_mapper.map_to_dict(b) for b in items[start:start + size]],
        )