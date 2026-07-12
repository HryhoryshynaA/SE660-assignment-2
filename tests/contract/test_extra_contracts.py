import pytest
from jsonschema import validate
from tests.builders.author_builder import AuthorBuilder
from tests.builders.book_builder import BookBuilder

PAGE_CONTRACT = {
    "type": "object",
    "properties": {
        "data": {"type": "array"},
        "pagination": {
            "type": "object",
            "properties": {
                "size": {"type": "integer"},
                "page": {"type": "integer"},
                "totalPages": {"type": "integer"},
                "hasNext": {"type": "boolean"},
                "hasPrevious": {"type": "boolean"}
            },
            "required": ["size", "page", "totalPages"]
        }
    },
    "required": ["data", "pagination"],
    "additionalProperties": False
}

ERROR_CONTRACT = {
    "type": "object",
    "properties": {
        "error": {"type": "string"},
        "message": {"type": "string"},
        "details": {"type": "array", "items": {"type": "string"}}  # optional
    },
    "required": ["error", "message"]
}

def test_pagination_contract_for_books(client):
    author_payload = AuthorBuilder().as_payload()
    author_response = client.post('/api/authors', json=author_payload)
    author_id = author_response.get_json()['id']

    for i in range(3):
        book_payload = (BookBuilder()
                        .with_author_id(author_id)
                        .with_title(f"Book Volume {i}")
                        .as_payload())
        client.post('/api/books', json=book_payload)

    response = client.get('/api/books?page=1&size=2')
    assert response.status_code == 200

    response_data = response.get_json()
    validate(instance=response_data, schema=PAGE_CONTRACT)
    assert response_data['pagination']['page'] == 1
    assert response_data['pagination']['size'] == 2
    assert response_data['pagination']['totalPages'] == 2
    assert len(response_data['data']) == 2


def test_author_deletion_conflict_contract(client):
    author_payload = AuthorBuilder().as_payload()
    author_response = client.post('/api/authors', json=author_payload)
    author_id = author_response.get_json()['id']

    book_payload = (BookBuilder()
                    .with_author_id(author_id)
                    .with_title("Dependent Book")
                    .as_payload())
    client.post('/api/books', json=book_payload)

    delete_response = client.delete(f'/api/authors/{author_id}')
    assert delete_response.status_code == 409

    error_data = delete_response.get_json()


    validate(instance=error_data, schema=ERROR_CONTRACT)
    assert error_data['error'] == 'CONFLICT'
    assert 'Cannot delete because author has' in error_data['message']