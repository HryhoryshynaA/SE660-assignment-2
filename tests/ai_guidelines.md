# Test Strategy for AI-Generated Unit Tests

## 1. Goal and scope

Generate unit tests for the `service` layer (`AuthorService`, `BookService`) and the `mapper`/`models` layer (`AuthorMapper`, `BookMapper`, `Page`). HTTP controllers, security, and API contracts are **out of scope**.

## 2. Testing level: bypass flask whenever possible

* Tests should target the service classes directly (`AuthorService()`, `BookService()`), without using `app.test_client()` or starting a Flask application.
* The HTTP layer (controllers) is not tested in this strategy, since it contains no business logic—only query parameter parsing and service invocation.

## 3. State isolation — mandatory

* Every test must start with a clean `_authors_db` and `_books_db`.
* Use the existing `autouse` fixture `reset_in_memory_db` from `tests/conftest.py`. **Do not create a new fixture** and do not rely on test execution order.
* Avoid assertions such as `len(_books_db) == 3` unless the test explicitly controls how many records existed before execution.

## 4. Test data construction - use test data builders only

* Use `BookBuilder` and `AuthorBuilder` from `tests/builders/`.
* Do not create ad hoc dictionary payloads if a builder already exists. If a required field or method is missing, **extend the builder** instead of bypassing it with a raw dictionary.
* The two terminal builder methods have distinct purposes:

  * `.as_payload()` -> used for `create_book`, `update_book`, and `_validate`
  * `.build_entity()` -> used to insert records directly into `_books_db` or `_authors_db`, bypassing service write methods when only read/filter behavior is being tested

## 5. Dependencies — use Stubs, not Mocking frameworks

* Replace `AuthorService` inside `BookService` with a minimal stub (`_AuthorServiceStub`) that provides a controlled implementation of `does_author_exists`, instead of using `unittest.mock.Mock()` or `MagicMock`. The stub explicitly documents the behavior required by the test.

## 6. Policy for known bugs

If a test encounters a known bug that blocks further execution:

1. Write a dedicated **regression test** that explicitly expects the current incorrect behavior using `pytest.raises(...)`, including a comment explaining the cause and its location in the source code.
2. Write a **second test** that bypasses the bug using `monkeypatch` so the remainder of the execution path can still be tested independently.
3. Do **not** skip testing downstream logic simply because an earlier bug prevents normal execution.

## 7. File structure

Create one file per "service + concern" rather than one large file per class.

```text
tests/unit/book/test_book_service_validation.py      # already exists
tests/unit/book/test_book_service_create.py          # already exists
tests/unit/book/test_book_service_query.py           # already exists
tests/unit/book/test_book_service_update.py          # NEW — cover update_book
tests/unit/book/test_book_mapper.py                  # NEW
tests/unit/author/test_author_service_validation.py  # NEW
tests/unit/author/test_author_service_crud.py        # NEW
tests/unit/author/test_author_mapper.py              # NEW
tests/unit/test_page_pagination.py                   # NEW
```

## 8. Required Scenario Classes for Every Public Method

For every service method that accepts input data, cover at least:

* Happy path (valid input -> successful execution)
* One test for each independent validation branch (rather than one test where everything is invalid simultaneously)
* Boundary values: `0`, negative values, maximum + 1, empty string, and `None`
* Side effects: verify whether data was (or was not) actually written to the in-memory database

For pagination (`Page`, `get_books`, `get_authors`), always cover:

* Exactly one page (fewer records than `size`)
* Exactly one full page (`records == size`, `hasNext == False`)
* First page (`hasPrevious == False`) and last page (`hasNext == False`)
* Empty collection (`total_pages == 1`, not `0`)

## 9. Prohibited practices

* Testing everything through a single "happy path" helper that all other tests depend on
* Duplicating setup code instead of using builders or fixtures
* Leaving "boring" branches untested (e.g., get-by-id not found, delete not found, empty list), as these are often the source of production defects
* Writing security tests within this strategy (security is outside its scope)

## 10. Success Criteria

A single AI generation is considered successful if, after the first execution:

* There are **0 unexpected test failures** (regression tests for known bugs are expected and do not count as unexpected failures)
* Coverage for every newly tested file under `application/` is **at least 90%**
