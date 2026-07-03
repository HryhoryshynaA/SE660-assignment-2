import uuid
from dataclasses import dataclass

VALID_GENRES   = {'FICTION', 'NON_FICTION', 'TECHNICAL', 'SCIENCE', 'HISTORY', 'OTHER'}
VALID_STATUSES = {'UNREAD', 'IN_PROGRESS', 'FINISHED'}

@dataclass
class Book:
    id: uuid.UUID
    user_id: uuid.UUID
    author_id: uuid.UUID
    series_id: uuid.UUID
    volume_number: int
    title: str
    genre: str
    published_year: int
    total_pages: int
    pages_read: int
    status: str
    created_at: str
    updated_at: str