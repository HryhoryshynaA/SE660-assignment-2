from application.models import Page

class TestPagePagination:

    def test_single_partial_page_has_no_next_or_previous(self):
        page = Page(size=10, page=1, total_pages=1, content=['a', 'b', 'c'])

        result = page.to_json()

        assert result['pagination']['hasNext'] is False
        assert result['pagination']['hasPrevious'] is False

    def test_first_page_of_many_has_next_but_not_previous(self):
        page = Page(size=2, page=1, total_pages=3, content=['a', 'b'])

        result = page.to_json()

        assert result['pagination']['hasNext'] is True
        assert result['pagination']['hasPrevious'] is False

    def test_middle_page_has_both_next_and_previous(self):
        page = Page(size=2, page=2, total_pages=3, content=['c', 'd'])

        result = page.to_json()

        assert result['pagination']['hasNext'] is True
        assert result['pagination']['hasPrevious'] is True

    def test_last_page_has_previous_but_not_next(self):
        page = Page(size=2, page=3, total_pages=3, content=['e'])

        result = page.to_json()

        assert result['pagination']['hasNext'] is False
        assert result['pagination']['hasPrevious'] is True

    def test_empty_content_still_produces_valid_pagination_block(self):
        page = Page(size=20, page=1, total_pages=1, content=[])

        result = page.to_json()

        assert result['data'] == []
        assert result['pagination']['hasNext'] is False
        assert result['pagination']['hasPrevious'] is False

    def test_print_content_outputs_content_to_stdout(self, capsys):
        page = Page(size=10, page=1, total_pages=1, content=['x'])
        page.print_content()

        captured = capsys.readouterr()
        assert "['x']" in captured.out

    def test_to_json_data_matches_content_length(self):
        page = Page(size=10, page=1, total_pages=1, content=['x', 'y', 'z'])

        result = page.to_json()

        assert len(result['data']) == 3