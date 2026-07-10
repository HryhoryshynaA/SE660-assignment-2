import pytest
from application.author.author_service import AuthorService
from tests.builders.author_builder import AuthorBuilder

class TestAuthorServiceValidation:

    def setup_method(self):
        self.service = AuthorService()

    def test_valid_payload_produces_no_errors(self):
        errors = self.service._validate(AuthorBuilder().as_payload())
        assert errors == []

    def test_missing_first_name_is_reported(self):
        payload = AuthorBuilder().without('firstName').as_payload()
        errors = self.service._validate(payload)
        assert any('firstName' in e for e in errors)

    def test_empty_first_name_is_reported(self):
        payload = AuthorBuilder().with_first_name('').as_payload()
        errors = self.service._validate(payload)
        assert any('firstName' in e for e in errors)

    def test_first_name_over_100_chars_is_rejected(self):
        payload = AuthorBuilder().with_first_name('x' * 101).as_payload()
        errors = self.service._validate(payload)
        assert any('firstName' in e for e in errors)

    def test_missing_last_name_is_reported(self):
        payload = AuthorBuilder().without('lastName').as_payload()
        errors = self.service._validate(payload)
        assert any('lastName' in e for e in errors)

    def test_last_name_over_100_chars_is_rejected(self):
        payload = AuthorBuilder().with_last_name('y' * 101).as_payload()
        errors = self.service._validate(payload)
        assert any('lastName' in e for e in errors)

    def test_nationality_over_100_chars_is_rejected(self):
        payload = AuthorBuilder().with_nationality('z' * 101).as_payload()
        errors = self.service._validate(payload)
        assert any('nationality' in e for e in errors)

    def test_nationality_is_optional(self):
        payload = AuthorBuilder().without('nationality').as_payload()
        errors = self.service._validate(payload)
        assert errors == []

    def test_multiple_errors_reported_together(self):
        payload = AuthorBuilder().with_first_name('').with_last_name('').as_payload()
        errors = self.service._validate(payload)
        assert len(errors) >= 2