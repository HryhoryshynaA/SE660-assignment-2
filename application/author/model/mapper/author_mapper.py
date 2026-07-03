import uuid
from datetime import datetime, timezone
from application.author.model.dto.author import Author

class AuthorMapper:

    def map_request(self, request_data) -> Author:
        return Author(
            id = request_data.get('id') or uuid.uuid4(),
            first_name = request_data.get('firstName'),
            last_name = request_data.get('lastName'),
            nationality = request_data.get('nationality'),
            created_at = datetime.now(timezone.utc).isoformat(),
        )

    def map_entity_to_dto(self, entity) -> Author:
        return Author(
            id = entity.id,
            first_name = entity.first_name,
            last_name = entity.last_name,
            nationality = entity.nationality,
            created_at = entity.created_at,
        )

    def map_to_dict(self, author: Author) -> dict:
        return {
            'id': str(author.id),
            'firstName': author.first_name,
            'lastName': author.last_name,
            'nationality': author.nationality,
            'createdAt': author.created_at,
        }