"""Tests for type definitions."""

from stream_chat.types.base import ParsedPredefinedFilterResponse, SortOrder, SortParam


class TestParsedPredefinedFilterResponse:
    """Tests for ParsedPredefinedFilterResponse type."""

    def test_type_definition(self):
        """Test that ParsedPredefinedFilterResponse can be used as a type hint."""
        response: ParsedPredefinedFilterResponse = {
            "name": "user_messaging",
            "filter": {"type": "messaging", "members": {"$in": ["user123"]}},
            "sort": [{"field": "last_message_at", "direction": SortOrder.DESC}],
        }

        assert response["name"] == "user_messaging"
        assert response["filter"]["type"] == "messaging"
        assert response["sort"][0]["field"] == "last_message_at"
        assert response["sort"][0]["direction"] == SortOrder.DESC

    def test_optional_sort(self):
        """Test that sort is optional in ParsedPredefinedFilterResponse."""
        response: ParsedPredefinedFilterResponse = {
            "name": "simple_filter",
            "filter": {"type": "messaging"},
        }

        assert response["name"] == "simple_filter"
        assert "sort" not in response

    def test_empty_filter(self):
        """Test that filter can be empty dict."""
        response: ParsedPredefinedFilterResponse = {
            "name": "empty_filter",
            "filter": {},
        }

        assert response["filter"] == {}


class TestSortParam:
    """Tests for SortParam type."""

    def test_ascending_sort(self):
        """Test ascending sort parameter."""
        sort: SortParam = {
            "field": "created_at",
            "direction": SortOrder.ASC,
        }

        assert sort["field"] == "created_at"
        assert sort["direction"] == 1

    def test_descending_sort(self):
        """Test descending sort parameter."""
        sort: SortParam = {
            "field": "last_message_at",
            "direction": SortOrder.DESC,
        }

        assert sort["field"] == "last_message_at"
        assert sort["direction"] == -1
