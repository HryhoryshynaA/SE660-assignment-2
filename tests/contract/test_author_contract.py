from jsonschema import validate
from tests.builders.author_builder import AuthorBuilder
from tests.conftest import AUTHOR_CONTRACT


def test_create_and_get_author_contract(client):
    payload = AuthorBuilder().with_first_name("Taras").with_last_name("Shevchenko").as_payload()

    response = client.post('/api/authors', json=payload)
    assert response.status_code == 201
    response_data = response.get_json()
    validate(instance=response_data, schema=AUTHOR_CONTRACT)
    author_id = response_data['id']
    assert response_data['firstName'] == "Taras"
    get_response = client.get(f'/api/authors/{author_id}')
    assert get_response.status_code == 200

    get_data = get_response.get_json()
    validate(instance=get_data, schema=AUTHOR_CONTRACT)
    assert get_data['id'] == author_id


def test_create_author_validation_error_contract(client):
    payload = AuthorBuilder().with_first_name("").as_payload()

    response = client.post('/api/authors', json=payload)
    assert response.status_code == 400

    error_data = response.get_json()
    assert error_data['error'] == 'VALIDATION_ERROR'
    assert 'firstName must be 1–100 characters' in error_data['details']