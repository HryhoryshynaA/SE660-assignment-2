import uuid

from application.book.model.mapper.book_mapper import BookMapper
from tests.builders.book_builder import BookBuilder


class TestBookMapperMapRequest:

    def setup_method(self):
        self.mapper = BookMapper()

    def test_map_request_creates_book_with_new_id_when_not_provided(self):
        payload = BookBuilder().as_payload()

        book = self.mapper.map_request(payload)

        assert isinstance(book.id, uuid.UUID)

    def test_map_request_uses_provided_id(self):
        fixed_id = str(uuid.uuid4())
        payload = BookBuilder().as_payload()
        payload['id'] = fixed_id

        book = self.mapper.map_request(payload)

        assert str(book.id) == fixed_id
        assert not isinstance(book.id, uuid.UUID)

    def test_map_request_defaults_pages_read_to_zero_when_absent(self):
        payload = BookBuilder().as_payload()
        assert 'pagesRead' not in payload

        book = self.mapper.map_request(payload)

        assert book.pages_read == 0

    def test_map_request_sets_series_and_volume_when_provided(self):
        series_id = uuid.uuid4()
        payload = BookBuilder().with_series(series_id=series_id, volume_number=3).as_payload()

        book = self.mapper.map_request(payload)

        assert book.series_id == series_id
        assert book.volume_number == 3

    def test_map_request_leaves_series_none_when_not_provided(self):
        payload = BookBuilder().as_payload()

        book = self.mapper.map_request(payload)

        assert book.series_id is None
        assert book.volume_number is None

    def test_map_request_always_sets_initial_status_unread(self):
        payload = BookBuilder().as_payload()

        book = self.mapper.map_request(payload)

        assert book.status == 'UNREAD'


class TestBookMapperEntityConversions:

    def setup_method(self):
        self.mapper = BookMapper()

    def test_map_entity_to_dto_preserves_all_fields(self):
        entity = BookBuilder().with_title('Round Trip').with_pages_read(10).build_entity()

        dto = self.mapper.map_entity_to_dto(entity)

        assert dto.id == entity.id
        assert dto.title == entity.title
        assert dto.pages_read == entity.pages_read

    def test_map_to_dict_uses_camel_case_keys(self):
        entity = BookBuilder().with_title('Dict Form').build_entity()

        result = self.mapper.map_to_dict(entity)

        assert result['title'] == 'Dict Form'
        assert 'publishedYear' in result
        assert 'totalPages' in result
        assert 'pagesRead' in result

    def test_map_to_dict_serializes_uuid_fields_as_strings(self):
        entity = BookBuilder().build_entity()

        result = self.mapper.map_to_dict(entity)

        assert isinstance(result['id'], str)
        assert isinstance(result['authorId'], str)

    def test_map_to_dict_returns_none_for_absent_series_fields(self):
        entity = BookBuilder().build_entity()

        result = self.mapper.map_to_dict(entity)

        assert result['seriesId'] is None
        assert result['volumeNumber'] is None