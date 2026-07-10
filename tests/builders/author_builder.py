class AuthorBuilder:
    def __init__(self):
        self._fields = {
            'firstName': 'Jane',
            'lastName': 'Doe',
            'nationality': 'American',
        }

    def with_first_name(self, first_name):
        self._fields['firstName'] = first_name
        return self

    def with_last_name(self, last_name):
        self._fields['lastName'] = last_name
        return self

    def with_nationality(self, nationality):
        self._fields['nationality'] = nationality
        return self

    def without(self, field_name):
        self._fields.pop(field_name, None)
        return self

    def as_payload(self) -> dict:
        return dict(self._fields)