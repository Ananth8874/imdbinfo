#!/usr/bin/env python
"""
Tests to verify AWS WAF bypass implementation.
Verifies that Chrome impersonation is used for all HTML GET requests.
"""
import os
import sys
from types import SimpleNamespace

# Ensure curl_cffi is available even without the real library installed.
if "curl_cffi" not in sys.modules:
    _mock_cffi_requests = SimpleNamespace(get=lambda *args, **kwargs: None)
    sys.modules["curl_cffi"] = SimpleNamespace(requests=_mock_cffi_requests)
    sys.modules["curl_cffi.requests"] = _mock_cffi_requests

from imdbinfo import services

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "tests", "sample_json_source")


def _load_sample_html(filename: str) -> bytes:
    with open(os.path.join(SAMPLE_DIR, filename), encoding="utf-8") as f:
        json_text = f.read()
    return f'<html><script id="__NEXT_DATA__">{json_text}</script></html>'.encode("utf-8")


def _mock_get_with_capture(filename: str):
    """Return a mock_get function and a dict that records call kwargs."""
    html = _load_sample_html(filename)
    captured = {}

    def mock_get(*args, **kwargs):
        captured.update(kwargs)
        return SimpleNamespace(status_code=200, content=html)

    return mock_get, captured


def test_waf_bypass_uses_chrome_impersonation(monkeypatch):
    """Search requests must use impersonate='chrome' to bypass AWS WAF."""
    mock_get, captured = _mock_get_with_capture("sample_search.json")
    monkeypatch.setattr(services.cffi_requests, "get", mock_get)
    services.search_title.cache_clear()

    results = services.search_title("little house on the prairie")

    assert captured.get("impersonate") == "chrome", (
        f"Expected impersonate='chrome', got {captured.get('impersonate')!r}"
    )
    assert results is not None
    assert len(results.titles) > 0


def test_multiple_searches_all_use_chrome_impersonation(monkeypatch):
    """Every search request must use impersonate='chrome', not just the first one."""
    html = _load_sample_html("sample_search.json")
    impersonations = []

    def mock_get(*args, **kwargs):
        impersonations.append(kwargs.get("impersonate"))
        return SimpleNamespace(status_code=200, content=html)

    monkeypatch.setattr(services.cffi_requests, "get", mock_get)
    services.search_title.cache_clear()

    for query in ("breaking bad", "the godfather"):
        result = services.search_title(query)
        assert result is not None, f"search_title('{query}') returned None"
        assert len(result.titles) > 0, f"No titles found for '{query}'"

    assert impersonations == ["chrome", "chrome"], (
        f"Expected all calls to use chrome impersonation, got {impersonations}"
    )


def test_get_movie_uses_chrome_impersonation(monkeypatch):
    """Movie detail requests must also use impersonate='chrome'."""
    mock_get, captured = _mock_get_with_capture("sample_resource.json")
    monkeypatch.setattr(services.cffi_requests, "get", mock_get)
    services.get_movie.cache_clear()

    movie = services.get_movie("tt0133093")

    assert captured.get("impersonate") == "chrome", (
        f"Expected impersonate='chrome', got {captured.get('impersonate')!r}"
    )
