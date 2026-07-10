import uuid
from application.author.model.mapper.author_mapper import AuthorMapper
from tests.builders.author_builder import AuthorBuilder


class TestAuthorMapper:

    def setup_method(self):
        self.mapper = AuthorMapper()

    def test_map_request_creates_author_with_new_id_when_not_provided(self):
        author = self.mapper.map_request(AuthorBuilder().as_payload())
        assert isinstance(author.id, uuid.UUID)

    def test_map_request_uses_provided_id(self):
        fixed_id = str(uuid.uuid4())
        payload = AuthorBuilder().as_payload()
        payload['id'] = fixed_id

        author = self.mapper.map_request(payload)

        assert str(author.id) == fixed_id
        assert not isinstance(author.id, uuid.UUID)

    def test_map_request_sets_created_at_timestamp(self):
        author = self.mapper.map_request(AuthorBuilder().as_payload())
        assert author.created_at  # непорожній ISO-рядок

    def test_map_entity_to_dto_preserves_fields(self):
        entity = self.mapper.map_request(AuthorBuilder().with_first_name('Ann').as_payload())

        dto = self.mapper.map_entity_to_dto(entity)

        assert dto.first_name == 'Ann'
        assert dto.id == entity.id

    def test_map_to_dict_uses_camel_case_keys(self):
        entity = self.mapper.map_request(AuthorBuilder().with_first_name('Ann').as_payload())

        result = self.mapper.map_to_dict(entity)

        assert result['firstName'] == 'Ann'
        assert 'createdAt' in result

    def test_map_to_dict_serializes_id_as_string(self):
        entity = self.mapper.map_request(AuthorBuilder().as_payload())

        result = self.mapper.map_to_dict(entity)

        assert isinstance(result['id'], str)

    def test_map_to_dict_allows_none_nationality(self):
        entity = self.mapper.map_request(AuthorBuilder().without('nationality').as_payload())

        result = self.mapper.map_to_dict(entity)

        assert result['nationality'] is None