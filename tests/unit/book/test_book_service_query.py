import uuid

from application.book.book_service import BookService, BookFilters, _books_db
from tests.builders.book_builder import BookBuilder


def seed(builder: BookBuilder):
    book = builder.build_entity()
    _books_db[str(book.id)] = book
    return book


class TestBookServiceQueryAndFilter:
    def setup_method(self):
        self.service = BookService()

    def test_get_books_filters_by_genre(self):
        seed(BookBuilder().with_title('Sci Book').with_genre('SCIENCE'))
        seed(BookBuilder().with_title('Fiction Book').with_genre('FICTION'))

        result = self.service.get_books(
            BookFilters(genre='SCIENCE', status=None, author_id=None,
                        published_year_from=None, published_year_to=None),
            page=1, size=20,
        )

        titles = [b['title'] for b in result.content]
        assert titles == ['Sci Book']

    def test_get_books_filters_by_status(self):
        seed(BookBuilder().with_title('Finished Book').with_status('FINISHED'))
        seed(BookBuilder().with_title('Unread Book').with_status('UNREAD'))

        result = self.service.get_books(
            BookFilters(genre=None, status='FINISHED', author_id=None, published_year_from=None, published_year_to=None), page=1, size=20,)

        assert len(result.content) == 1
        assert result.content[0]['title'] == 'Finished Book'

    def test_get_books_filters_by_published_year_range(self):
        seed(BookBuilder().with_title('Old Book').with_published_year(1950))
        seed(BookBuilder().with_title('New Book').with_published_year(2020))
        seed(BookBuilder().with_title('Mid Book').with_published_year(1990))

        result = self.service.get_books(
            BookFilters(genre=None, status=None, author_id=None,
                        published_year_from=1980, published_year_to=2000),
            page=1, size=20,
        )

        titles = {b['title'] for b in result.content}
        assert titles == {'Mid Book'}

    def test_get_books_filters_by_author_id(self):
        author_a = uuid.uuid4()
        author_b = uuid.uuid4()
        seed(BookBuilder().with_title('By A').with_author_id(author_a))
        seed(BookBuilder().with_title('By B').with_author_id(author_b))

        result = self.service.get_books(
            BookFilters(genre=None, status=None, author_id=str(author_a),
                        published_year_from=None, published_year_to=None),
            page=1, size=20,
        )

        assert len(result.content) == 1
        assert result.content[0]['title'] == 'By A'

    def test_get_books_sorts_by_title_ascending_by_default(self):
        seed(BookBuilder().with_title('Zebra'))
        seed(BookBuilder().with_title('Apple'))
        seed(BookBuilder().with_title('Mango'))

        result = self.service.get_books(
            BookFilters(None, None, None, None, None), page=1, size=20,
        )

        titles = [b['title'] for b in result.content]
        assert titles == sorted(titles)

    def test_get_books_sorts_by_published_year_descending(self):
        seed(BookBuilder().with_title('First').with_published_year(2000))
        seed(BookBuilder().with_title('Second').with_published_year(2020))
        seed(BookBuilder().with_title('Third').with_published_year(2010))

        result = self.service.get_books(
            BookFilters(None, None, None, None, None),
            page=1, size=20, sort='publishedYear', order='desc',
        )

        years = [b['publishedYear'] for b in result.content]
        assert years == sorted(years, reverse=True)

    def test_get_books_pagination_second_page(self):
        for i in range(5):
            seed(BookBuilder().with_title(f'Book {i}'))

        page1 = self.service.get_books(BookFilters(None, None, None, None, None), page=1, size=2)
        page2 = self.service.get_books(BookFilters(None, None, None, None, None), page=2, size=2)

        assert len(page1.content) == 2
        assert len(page2.content) == 2
        assert page1.content != page2.content
        assert page1.total_pages == 3

    def test_get_books_pagination_metadata_has_next_and_previous(self):
        for i in range(5):
            seed(BookBuilder().with_title(f'Book {i}'))

        page = self.service.get_books(BookFilters(None, None, None, None, None), page=2, size=2)
        page_json = page.to_json()['pagination']

        assert page_json['hasNext'] is True
        assert page_json['hasPrevious'] is True

    def test_get_books_empty_db_returns_empty_page_with_total_pages_one(self):
        result = self.service.get_books(BookFilters(None, None, None, None, None), page=1, size=20)

        assert result.content == []
        assert result.total_pages == 1


class TestBookServiceDeleteAndLookup:

    def setup_method(self):
        self.service = BookService()

    def test_delete_book_removes_existing_book(self):
        book = seed(BookBuilder().with_title('To Remove'))

        deleted = self.service.delete_book(str(book.id))

        assert deleted is True
        assert str(book.id) not in _books_db

    def test_delete_book_returns_false_for_missing_book(self):
        deleted = self.service.delete_book('nonexistent-id')
        assert deleted is False

    def test_books_by_author_returns_only_matching_books(self):
        author_a = uuid.uuid4()
        author_b = uuid.uuid4()
        seed(BookBuilder().with_title('A1').with_author_id(author_a))
        seed(BookBuilder().with_title('A2').with_author_id(author_a))
        seed(BookBuilder().with_title('B1').with_author_id(author_b))

        result = self.service.books_by_author(str(author_a))

        assert len(result) == 2
        assert all(str(b.author_id) == str(author_a) for b in result)

    def test_books_by_author_returns_empty_list_when_no_books(self):
        result = self.service.books_by_author(str(uuid.uuid4()))
        assert result == []

    def test_get_book_returns_none_for_missing_id(self):
        assert self.service.get_book('nonexistent-id') is None