import uuid
from jsonschema import validate
from tests.builders.author_builder import AuthorBuilder
from tests.builders.book_builder import BookBuilder
from tests.conftest import BOOK_CONTRACT

def test_book_lifecycle_and_status_contract(client):
    author_payload = AuthorBuilder().as_payload()
    author_response = client.post('/api/authors', json=author_payload)
    author_id = author_response.get_json()['id']

    book_payload = (BookBuilder()
                    .with_author_id(author_id)
                    .with_title("Kobzar")
                    .with_genre("FICTION")
                    .with_total_pages(300)
                    .with_pages_read(0)
                    .as_payload())

    book_response = client.post('/api/books', json=book_payload)
    assert book_response.status_code == 201

    book_data = book_response.get_json()
    validate(instance=book_data, schema=BOOK_CONTRACT)
    assert book_data['status'] == 'UNREAD'
    book_id = book_data['id']

    update_payload = book_payload.copy()
    update_payload['pagesRead'] = 300
    update_response = client.put(f'/api/books/{book_id}', json=update_payload)
    assert update_response.status_code == 200

    updated_data = update_response.get_json()
    validate(instance=updated_data, schema=BOOK_CONTRACT)

    assert updated_data['status'] == 'FINISHED'

def test_create_book_with_nonexistent_author_contract(client):
    fake_author_id = str(uuid.uuid4())
    book_payload = BookBuilder().with_author_id(fake_author_id).as_payload()

    response = client.post('/api/books', json=book_payload)

    assert response.status_code == 400
    error_data = response.get_json()
    assert error_data['error'] == 'VALIDATION_ERROR'
    assert f'authorId {fake_author_id} not exist' in error_data['details']