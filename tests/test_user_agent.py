"""Tests for USER_AGENT configuration and error messages."""

import pytest
from types import SimpleNamespace
from imdbinfo import services


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_get(captured_headers: dict):
    """Return a niquests.get mock that records request headers."""
    def mock_get(url, headers=None, **kwargs):
        captured_headers.update(headers or {})
        html_bytes = (
            b'<html><script id="__NEXT_DATA__">'
            b'{"props":{"pageProps":{"aboveTheFoldData":{"id":"tt0133093"}}}}'
            b'</script></html>'
        )
        return SimpleNamespace(status_code=200, content=html_bytes)
    return mock_get


# ---------------------------------------------------------------------------
# Basic existence
# ---------------------------------------------------------------------------

def test_user_agent_is_defined():
    """Test that USER_AGENTS_LIST module variable is defined."""
    assert hasattr(services, "USER_AGENTS_LIST")
    assert isinstance(services.USER_AGENTS_LIST, list)
    assert len(services.USER_AGENTS_LIST) > 0


# ---------------------------------------------------------------------------
# Override mechanism — correctness & state safety
# ---------------------------------------------------------------------------

def test_user_agent_can_be_overridden(monkeypatch):
    """USER_AGENTS_LIST override is respected — uses monkeypatch for safe cleanup."""
    custom_ua = "CustomUserAgent/1.0"
    # Use monkeypatch so the list is always restored, even on test failure
    monkeypatch.setattr(services, "USER_AGENTS_LIST", [custom_ua])

    captured_headers = {}
    monkeypatch.setattr(services.niquests, "get", _make_mock_get(captured_headers))

    services.get_movie.cache_clear()
    try:
        services.get_movie("tt0133093")
    except Exception:
        pass  # only care about captured headers

    assert captured_headers.get("User-Agent") == custom_ua


def test_override_single_item_always_uses_that_ua(monkeypatch):
    """Single-item override list must always produce exactly that UA string."""
    only_ua = "OnlyAgent/9.9"
    monkeypatch.setattr(services, "USER_AGENTS_LIST", [only_ua])

    seen = set()
    captured_headers = {}
    monkeypatch.setattr(services.niquests, "get", _make_mock_get(captured_headers))

    for _ in range(10):
        services.get_movie.cache_clear()
        captured_headers.clear()
        try:
            services.get_movie("tt0133093")
        except Exception:
            pass
        ua = captured_headers.get("User-Agent")
        if ua:
            seen.add(ua)

    assert seen == {only_ua}, f"Expected only '{only_ua}', got {seen}"


def test_override_multi_item_uses_only_list_values(monkeypatch):
    """Multi-item override list must only produce UAs from that list."""
    custom_list = ["AgentA/1.0", "AgentB/2.0", "AgentC/3.0"]
    monkeypatch.setattr(services, "USER_AGENTS_LIST", custom_list)

    seen = set()
    captured_headers = {}
    monkeypatch.setattr(services.niquests, "get", _make_mock_get(captured_headers))

    for _ in range(20):
        services.get_movie.cache_clear()
        captured_headers.clear()
        try:
            services.get_movie("tt0133093")
        except Exception:
            pass
        ua = captured_headers.get("User-Agent")
        if ua:
            seen.add(ua)

    assert seen.issubset(set(custom_list)), (
        f"Got UAs outside the custom list: {seen - set(custom_list)}"
    )


def test_default_list_not_polluted_after_override(monkeypatch):
    """After an override via monkeypatch, the default list must be intact."""
    original_list = list(services.USER_AGENTS_LIST)
    default_list = list(services._DEFAULT_USER_AGENTS_LIST)

    monkeypatch.setattr(services, "USER_AGENTS_LIST", ["TempAgent/1.0"])
    # monkeypatch restores automatically — simulate end-of-test restore
    monkeypatch.undo()

    assert services.USER_AGENTS_LIST == original_list, (
        "USER_AGENTS_LIST was not restored after override"
    )
    assert services._DEFAULT_USER_AGENTS_LIST == default_list, (
        "_DEFAULT_USER_AGENTS_LIST must never be mutated"
    )


def test_override_does_not_affect_default_user_agents_list(monkeypatch):
    """Overriding USER_AGENTS_LIST must not mutate _DEFAULT_USER_AGENTS_LIST."""
    snapshot = list(services._DEFAULT_USER_AGENTS_LIST)
    monkeypatch.setattr(services, "USER_AGENTS_LIST", ["InjectedAgent/1.0"])
    assert services._DEFAULT_USER_AGENTS_LIST == snapshot


def test_request_handler_default_generates_fresh_ua(monkeypatch):
    """Without an override, request_handler must generate a fresh UA (not from default list)."""
    # Ensure USER_AGENTS_LIST equals the default so the 'else' branch is taken
    monkeypatch.setattr(services, "USER_AGENTS_LIST", list(services._DEFAULT_USER_AGENTS_LIST))

    generated_uas = set()

    def mock_get(url, headers=None, **kwargs):
        if headers and "User-Agent" in headers:
            generated_uas.add(headers["User-Agent"])
        return SimpleNamespace(
            status_code=200,
            content=(
                b'<html><script id="__NEXT_DATA__">'
                b'{"props":{"pageProps":{"aboveTheFoldData":{"id":"tt0133093"}}}}'
                b'</script></html>'
            ),
        )

    monkeypatch.setattr(services.niquests, "get", mock_get)

    for _ in range(10):
        services.get_movie.cache_clear()
        try:
            services.get_movie("tt0133093")
        except Exception:
            pass

    # All generated UAs must start with Mozilla/5.0 (engine-generated strings)
    for ua in generated_uas:
        assert ua.startswith("Mozilla/5.0"), f"Unexpected UA format: {ua}"


def test_error_message_includes_status_code(monkeypatch):
    """Test that error messages include HTTP status code."""

    def mock_get_with_error(*args, **kwargs):
        return SimpleNamespace(status_code=404, text="Not Found", content=b"Not Found")

    monkeypatch.setattr(services.niquests, "get", mock_get_with_error)

    with pytest.raises(Exception) as exc_info:
        services.get_movie.cache_clear()
        services.get_movie("tt9999999")

    # Check that the error message includes the status code
    assert "HTTP 404" in str(exc_info.value)
    assert "https://www.imdb.com" in str(exc_info.value)


def test_error_message_includes_response_text(monkeypatch):
    """Test that error messages include response text when available."""

    def mock_get_with_error(*args, **kwargs):
        return SimpleNamespace(
            status_code=500,
            text="Internal Server Error - Something went wrong",
            content=b"Internal Server Error",
        )

    monkeypatch.setattr(services.niquests, "get", mock_get_with_error)

    with pytest.raises(Exception) as exc_info:
        services.get_movie.cache_clear()
        services.get_movie("tt0133093")

    # Check that the error message includes both status code and response text
    error_msg = str(exc_info.value)
    assert "HTTP 500" in error_msg
    assert "Internal Server Error" in error_msg


def test_get_name_error_message_includes_details(monkeypatch):
    """Test that get_name error messages include HTTP details."""

    def mock_get_with_error(*args, **kwargs):
        return SimpleNamespace(status_code=403, text="Forbidden", content=b"Forbidden")

    monkeypatch.setattr(services.niquests, "get", mock_get_with_error)

    with pytest.raises(Exception) as exc_info:
        services.get_name.cache_clear()
        services.get_name("nm9999999")

    # Check that the error message includes the status code
    error_msg = str(exc_info.value)
    assert "HTTP 403" in error_msg
    assert "https://www.imdb.com" in error_msg


def test_get_season_episodes_error_message_includes_details(monkeypatch):
    """Test that get_season_episodes error messages include HTTP details."""

    def mock_get_with_error(*args, **kwargs):
        return SimpleNamespace(
            status_code=400, text="Bad Request", content=b"Bad Request"
        )

    monkeypatch.setattr(services.niquests, "get", mock_get_with_error)

    with pytest.raises(Exception) as exc_info:
        services.get_season_episodes.cache_clear()
        services.get_season_episodes("tt0133093", season=1)

    # Check that the error message includes the status code
    error_msg = str(exc_info.value)
    assert "HTTP 400" in error_msg
    assert "episodes" in error_msg


def test_graphql_error_message_includes_title_id():
    """Test that GraphQL error messages include the title/person ID."""
    # Since we can't easily mock post in the stubbed niquests module,
    # we test this directly by calling the function with a mocked module
    from types import SimpleNamespace

    # Save the original module
    original_niquests = services.niquests

    try:
        # Create a mock that has both get and post
        def mock_post_with_http_error(*args, **kwargs):
            return SimpleNamespace(
                status_code=500, text="Internal Server Error", json=lambda: {}
            )

        # Create new namespace with both get and post
        mock_niquests = SimpleNamespace(
            get=original_niquests.get, post=mock_post_with_http_error
        )

        # Replace the module
        services.niquests = mock_niquests

        with pytest.raises(Exception) as exc_info:
            services._get_extended_title_info.cache_clear()
            services._get_extended_title_info("0133093")

        # Check that the error message includes the IMDb ID and HTTP status
        error_msg = str(exc_info.value)
        assert "tt0133093" in error_msg
        assert "HTTP 500" in error_msg
    finally:
        # Restore original module
        services.niquests = original_niquests


def test_graphql_error_response_includes_details():
    """Test that GraphQL error responses include error details."""
    from types import SimpleNamespace

    # Save the original module
    original_niquests = services.niquests

    try:
        # Create a mock that returns GraphQL errors
        def mock_post_with_graphql_error(*args, **kwargs):
            return SimpleNamespace(
                status_code=200,
                text="OK",
                json=lambda: {"errors": [{"message": "Invalid ID"}]},
            )

        # Create new namespace with both get and post
        mock_niquests = SimpleNamespace(
            get=original_niquests.get, post=mock_post_with_graphql_error
        )

        # Replace the module
        services.niquests = mock_niquests

        with pytest.raises(Exception) as exc_info:
            services._get_extended_title_info.cache_clear()
            services._get_extended_title_info("0133093")

        # Check that the error message includes the IMDb ID and GraphQL error details
        error_msg = str(exc_info.value)
        assert "tt0133093" in error_msg
        assert "GraphQL error" in error_msg
    finally:
        # Restore original module
        services.niquests = original_niquests
