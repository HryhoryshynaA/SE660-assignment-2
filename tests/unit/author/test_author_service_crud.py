from application.author.author_service import AuthorService, AuthorFilters, _authors_db
from tests.builders.author_builder import AuthorBuilder

class TestAuthorServiceCreateGetDelete:

    def setup_method(self):
        self.service = AuthorService()

    def test_create_author_success_stores_and_returns_dict(self):
        payload = AuthorBuilder().with_first_name('George').with_last_name('Orwell').as_payload()

        result, errors = self.service.create_author(payload)

        assert errors is None
        assert result['firstName'] == 'George'
        assert result['id'] in _authors_db

    def test_create_author_with_invalid_data_returns_errors_and_does_not_store(self):
        before = len(_authors_db)
        payload = AuthorBuilder().without('firstName').as_payload()

        result, errors = self.service.create_author(payload)

        assert result is None
        assert errors is not None
        assert len(_authors_db) == before

    def test_get_author_returns_dict_for_existing_id(self):
        created, _ = self.service.create_author(AuthorBuilder().as_payload())

        result = self.service.get_author(created['id'])

        assert result['firstName'] == created['firstName']

    def test_get_author_returns_none_for_missing_id(self):
        assert self.service.get_author('nonexistent-id') is None

    def test_delete_author_removes_existing_author(self):
        created, _ = self.service.create_author(AuthorBuilder().as_payload())

        deleted = self.service.delete_author(created['id'])

        assert deleted is True
        assert created['id'] not in _authors_db

    def test_delete_author_returns_false_for_missing_author(self):
        assert self.service.delete_author('nonexistent-id') is False

    def test_does_author_exists_true_for_existing(self):
        created, _ = self.service.create_author(AuthorBuilder().as_payload())
        assert self.service.does_author_exists(created['id']) is True

    def test_does_author_exists_false_for_missing(self):
        assert self.service.does_author_exists('nonexistent-id') is False


class TestAuthorServiceUpdate:

    def setup_method(self):
        self.service = AuthorService()

    def test_update_author_success(self):
        created, _ = self.service.create_author(AuthorBuilder().with_first_name('Old').as_payload())
        payload = AuthorBuilder().with_first_name('New').as_payload()

        result, errors = self.service.update_author(created['id'], payload)

        assert errors is None
        assert result['firstName'] == 'New'

    def test_update_author_returns_none_none_for_missing_author(self):
        result, errors = self.service.update_author('nonexistent-id', AuthorBuilder().as_payload())
        assert result is None
        assert errors is None

    def test_update_author_with_invalid_data_returns_errors(self):
        created, _ = self.service.create_author(AuthorBuilder().as_payload())
        payload = AuthorBuilder().without('lastName').as_payload()

        result, errors = self.service.update_author(created['id'], payload)

        assert result is None
        assert errors is not None


class TestAuthorServiceGetAuthorsListing:

    def setup_method(self):
        self.service = AuthorService()

    def _seed(self, first_name, last_name):
        created, _ = self.service.create_author(AuthorBuilder().with_first_name(first_name).with_last_name(last_name).as_payload())
        return created

    def test_get_authors_sorted_by_last_name_ascending(self):
        self._seed('A', 'Zebra')
        self._seed('B', 'Apple')
        self._seed('C', 'Mango')

        page = self.service.get_authors(AuthorFilters(search=None), page=1, size=20)

        last_names = [a['lastName'] for a in page.content]
        assert last_names == sorted(last_names)

    def test_get_authors_search_matches_first_or_last_name_case_insensitive(self):
        self._seed('George', 'Orwell')
        self._seed('Jane', 'Austen')

        page = self.service.get_authors(AuthorFilters(search='orwell'), page=1, size=20)

        assert len(page.content) == 1
        assert page.content[0]['lastName'] == 'Orwell'

    def test_get_authors_pagination_second_page(self):
        for i in range(5):
            self._seed(f'First{i}', f'Last{i}')

        page1 = self.service.get_authors(AuthorFilters(search=None), page=1, size=2)
        page2 = self.service.get_authors(AuthorFilters(search=None), page=2, size=2)

        assert len(page1.content) == 2
        assert len(page2.content) == 2
        assert page1.content != page2.content

    def test_get_authors_empty_db_returns_empty_page_with_total_pages_one(self):
        page = self.service.get_authors(AuthorFilters(search=None), page=1, size=20)

        assert page.content == []
        assert page.total_pages == 1

    def test_get_authors_falls_back_to_defaults_on_non_integer_page_or_size(self):
        self._seed('A', 'Author')
        page = self.service.get_authors(AuthorFilters(search=None), page='not-a-number', size='also-not')
        assert page.page == 1
        assert page.size == 20