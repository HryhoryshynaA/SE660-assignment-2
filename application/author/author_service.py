from application.author.model.dto.author import Author
from application.author.model.mapper.author_mapper import AuthorMapper
import math
from application.models import Page

_authors_db: dict[str, Author] = {}

class AuthorFilters:
    def __init__(self, search: str = None):
        self.search = search


class AuthorService:
    def __init__(self):
        self.mapper = AuthorMapper()

    def _validate(self, data: dict) -> list[str]:
        errors = []
        if not data.get('firstName') or not (1 <= len(data['firstName']) <= 100):
            errors.append('firstName must be 1–100 characters')
        if not data.get('lastName') or not (1 <= len(data['lastName']) <= 100):
            errors.append('lastName must be 1–100 characters')
        nationality = data.get('nationality')
        if nationality is not None and len(nationality) > 100:
            errors.append('nationality cannot be more than 100 characters')
        return errors

    def create_author(self, data: dict):
        errors = self._validate(data)

        if errors:
            return None, errors

        author = self.mapper.map_request(data)
        _authors_db[str(author.id)] = author
        return self.mapper.map_to_dict(author), None

    def get_author(self, author_id: str):
        author = _authors_db.get(author_id)

        if author is None:
            return None

        return self.mapper.map_to_dict(author)

    def get_authors(self, filters: AuthorFilters, page, size) -> Page:
        try:
            page = int(page) if page is not None else 1
            size = int(size) if size is not None else 20
        except ValueError:
            page, size = 1, 20

        items = list(_authors_db.values())

        if filters.search:
            q = filters.search.lower()
            items = [a for a in items
                     if q in a.first_name.lower() or q in a.last_name.lower()]

        items.sort(key=lambda a: a.last_name.lower())

        total_pages = max(1, math.ceil(len(items) / size))
        start = (page - 1) * size
        page_items = items[start:start + size]

        return Page(
            size=size,
            page=page,
            total_pages=total_pages,
            content=[self.mapper.map_to_dict(a) for a in page_items],
        )

    def update_author(self, author_id: str, data: dict):
        author = _authors_db.get(author_id)

        if author is None:
            return None, None

        errors = self._validate(data)

        if errors:
            return None, errors

        author.first_name = data['firstName']
        author.last_name = data['lastName']
        author.nationality = data.get('nationality')
        _authors_db[author_id] = author
        return self.mapper.map_to_dict(author), None

    def delete_author(self, author_id: str):
        if author_id not in _authors_db:
            return False
        del _authors_db[author_id]
        return True

    def does_author_exists(self, author_id: str):
        return author_id in _authors_db