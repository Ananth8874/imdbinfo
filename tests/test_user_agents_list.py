"""Tests for the user_agents_list engine module."""

import pytest
from imdbinfo.user_agents_list import (
    generate_user_agent_item,
    generate_user_agents_list,
    get_random_user_agent,
    _WINDOWS_PLATFORMS,
    _MAC_PLATFORMS,
    _LINUX_PLATFORMS,
)


# ---------------------------------------------------------------------------
# generate_user_agent_item
# ---------------------------------------------------------------------------

class TestGenerateUserAgentItem:
    def test_returns_string(self):
        ua = generate_user_agent_item()
        assert isinstance(ua, str)

    def test_not_empty(self):
        ua = generate_user_agent_item()
        assert len(ua) > 0

    def test_starts_with_mozilla(self):
        """All major browser UAs start with Mozilla/5.0."""
        for _ in range(20):
            ua = generate_user_agent_item()
            assert ua.startswith("Mozilla/5.0"), f"Unexpected UA prefix: {ua}"

    def test_contains_known_browser_token(self):
        """UA string must contain at least one known browser engine token."""
        known_tokens = ("AppleWebKit", "Gecko/20100101")
        for _ in range(20):
            ua = generate_user_agent_item()
            assert any(token in ua for token in known_tokens), (
                f"No known browser token found in: {ua}"
            )

    def test_contains_known_platform(self):
        """UA string must embed a platform from one of the known platform lists."""
        all_platforms = _WINDOWS_PLATFORMS + _MAC_PLATFORMS + _LINUX_PLATFORMS
        for _ in range(20):
            ua = generate_user_agent_item()
            assert any(p in ua for p in all_platforms), (
                f"No known platform found in: {ua}"
            )

    def test_each_call_can_produce_different_result(self):
        """Multiple calls should not always return the same string (probabilistic)."""
        results = {generate_user_agent_item() for _ in range(30)}
        assert len(results) > 1, "generate_user_agent_item returned the same string 30 times"

    def test_chrome_format(self, monkeypatch):
        """When Chrome builder is selected, UA must contain Chrome/ token."""
        from imdbinfo import user_agents_list as ual
        monkeypatch.setattr(
            ual.random, "choice",
            lambda seq: ual._build_chrome_user_agent if callable(seq[0]) else seq[0],
        )
        ua = ual.generate_user_agent_item()
        assert "Chrome/" in ua
        assert "Safari/537.36" in ua

    def test_firefox_format(self, monkeypatch):
        """When Firefox builder is selected, UA must contain Firefox/ token."""
        from imdbinfo import user_agents_list as ual

        monkeypatch.setattr(
            ual.random, "choice",
            lambda seq: ual._build_firefox_user_agent if callable(seq[0]) else seq[0],
        )
        ua = ual.generate_user_agent_item()
        assert "Firefox/" in ua
        assert "Gecko/20100101" in ua

    def test_edge_format(self, monkeypatch):
        """When Edge builder is selected, UA must contain Edg/ token."""
        from imdbinfo import user_agents_list as ual

        monkeypatch.setattr(
            ual.random, "choice",
            lambda seq: ual._build_edge_user_agent if callable(seq[0]) else seq[0],
        )
        ua = ual.generate_user_agent_item()
        assert "Edg/" in ua


# ---------------------------------------------------------------------------
# generate_user_agents_list — list size validation
# ---------------------------------------------------------------------------

class TestGenerateUserAgentsList:
    def test_default_size_is_eight(self):
        lst = generate_user_agents_list()
        assert len(lst) == 8

    def test_custom_size(self):
        for size in (1, 5, 20, 50):
            lst = generate_user_agents_list(size=size)
            assert len(lst) == size, f"Expected {size} items, got {len(lst)}"

    def test_returns_list_of_strings(self):
        lst = generate_user_agents_list(size=5)
        assert isinstance(lst, list)
        assert all(isinstance(ua, str) for ua in lst)

    def test_invalid_size_zero_raises(self):
        with pytest.raises(ValueError, match="size must be greater than 0"):
            generate_user_agents_list(size=0)

    def test_invalid_size_negative_raises(self):
        with pytest.raises(ValueError, match="size must be greater than 0"):
            generate_user_agents_list(size=-5)

    def test_items_are_non_empty_strings(self):
        lst = generate_user_agents_list(size=10)
        assert all(len(ua) > 0 for ua in lst)

    def test_list_items_start_with_mozilla(self):
        lst = generate_user_agents_list(size=10)
        assert all(ua.startswith("Mozilla/5.0") for ua in lst)


# ---------------------------------------------------------------------------
# get_random_user_agent — fallback behavior
# ---------------------------------------------------------------------------

class TestGetRandomUserAgent:
    def test_with_list_picks_from_list(self):
        fixed_list = ["AgentA/1.0", "AgentB/2.0", "AgentC/3.0"]
        for _ in range(30):
            ua = get_random_user_agent(fixed_list)
            assert ua in fixed_list

    def test_with_single_item_list_always_returns_that_item(self):
        fixed_list = ["OnlyAgent/1.0"]
        for _ in range(10):
            assert get_random_user_agent(fixed_list) == "OnlyAgent/1.0"

    def test_without_list_returns_generated_string(self):
        """Fallback: no list supplied → generates a fresh UA."""
        ua = get_random_user_agent()
        assert isinstance(ua, str)
        assert ua.startswith("Mozilla/5.0")

    def test_none_list_falls_back_to_generated(self):
        ua = get_random_user_agent(None)
        assert isinstance(ua, str)
        assert ua.startswith("Mozilla/5.0")

    def test_empty_list_falls_back_to_generated(self):
        """An empty list must not be used; fall back to generating a fresh UA."""
        ua = get_random_user_agent([])
        assert isinstance(ua, str)
        assert ua.startswith("Mozilla/5.0")

    def test_fallback_generates_different_values(self):
        """Fallback path should produce variability across calls (probabilistic)."""
        results = {get_random_user_agent() for _ in range(30)}
        assert len(results) > 1

