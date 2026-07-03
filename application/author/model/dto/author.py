import uuid
from dataclasses import dataclass

@dataclass
class Author:
    id: uuid.UUID
    first_name: str
    last_name: str
    nationality: str
    created_at: str