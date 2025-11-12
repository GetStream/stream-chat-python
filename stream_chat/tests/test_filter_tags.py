import pytest

from stream_chat.channel import Channel


@pytest.mark.incremental
class TestFilterTags:
    def test_add_and_remove_filter_tags(self, channel: Channel):
        # Add tags
        add_resp = channel.add_filter_tags(["vip", "premium"])
        assert "channel" in add_resp
        assert set(add_resp["channel"].get("filter_tags", [])) >= {"vip", "premium"}

        # Remove one tag
        remove_resp = channel.remove_filter_tags(["premium"])
        assert "channel" in remove_resp
        remaining = remove_resp["channel"].get("filter_tags", [])
        assert "premium" not in remaining
        assert "vip" in remaining
