from datetime import date, timedelta

import pytest

from stream_chat import StreamChat


class TestTeamUsageStats:
    def test_query_team_usage_stats_default(self, client: StreamChat):
        """Test querying team usage stats with default options."""
        response = client.query_team_usage_stats()
        assert "teams" in response
        assert isinstance(response["teams"], list)

    def test_query_team_usage_stats_with_month(self, client: StreamChat):
        """Test querying team usage stats with month parameter."""
        current_month = date.today().strftime("%Y-%m")
        response = client.query_team_usage_stats(month=current_month)
        assert "teams" in response
        assert isinstance(response["teams"], list)

    def test_query_team_usage_stats_with_date_range(self, client: StreamChat):
        """Test querying team usage stats with date range."""
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        response = client.query_team_usage_stats(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
        )
        assert "teams" in response
        assert isinstance(response["teams"], list)

    def test_query_team_usage_stats_with_pagination(self, client: StreamChat):
        """Test querying team usage stats with pagination."""
        response = client.query_team_usage_stats(limit=10)
        assert "teams" in response
        assert isinstance(response["teams"], list)

        # If there's a next cursor, test fetching the next page
        if response.get("next"):
            next_response = client.query_team_usage_stats(
                limit=10, next=response["next"]
            )
            assert "teams" in next_response
            assert isinstance(next_response["teams"], list)

    def test_query_team_usage_stats_response_structure(self, client: StreamChat):
        """Test that response contains expected metric fields when data exists."""
        # Query last year to maximize chance of getting data
        end_date = date.today()
        start_date = end_date - timedelta(days=365)
        response = client.query_team_usage_stats(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
        )

        assert "teams" in response
        teams = response["teams"]

        if teams:
            team = teams[0]
            # Verify team identifier
            assert "team" in team

            # Verify daily activity metrics
            assert "users_daily" in team
            assert "messages_daily" in team
            assert "translations_daily" in team
            assert "image_moderations_daily" in team

            # Verify peak metrics
            assert "concurrent_users" in team
            assert "concurrent_connections" in team

            # Verify rolling/cumulative metrics
            assert "users_total" in team
            assert "users_last_24_hours" in team
            assert "users_last_30_days" in team
            assert "users_month_to_date" in team
            assert "users_engaged_last_30_days" in team
            assert "users_engaged_month_to_date" in team
            assert "messages_total" in team
            assert "messages_last_24_hours" in team
            assert "messages_last_30_days" in team
            assert "messages_month_to_date" in team

            # Verify metric structure
            assert "total" in team["users_daily"]
