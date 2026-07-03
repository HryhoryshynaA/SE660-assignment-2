from typing import TypeVar, Generic, List
from dataclasses import asdict, is_dataclass

T = TypeVar('T')
class Page(Generic[T]):
    def __init__(self, size: int, page: int, total_pages: int, content: List[T]):
        self.size = size
        self.page = page
        self.total_pages = total_pages
        self.content = content

    def print_content(self):
        print(self.content)
        
    def to_json(self):
        def serialize(item):
            return asdict(item) if is_dataclass(item) else item

        return {
            'data': [serialize(item) for item in self.content],
            'pagination': {
                'page': self.page,
                'size': self.size,
                'totalPages': self.total_pages,
                'hasNext': self.page < self.total_pages,
                'hasPrevious': self.page > 1,
            }
        }