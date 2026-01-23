import os
from types import SimpleNamespace
from unittest.mock import Mock, patch
from imdbinfo import services


SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_json_source")


def load_sample_text(filename: str) -> str:
    with open(os.path.join(SAMPLE_DIR, filename), encoding="utf-8") as f:
        return f.read()


def mock_get_with_waf_challenge_factory(filename: str):
    """
    Factory that returns a mock function which:
    1. First returns a WAF challenge response
    2. On retry, returns the actual sample data
    """
    json_text = load_sample_text(filename)
    html = f'<html><script id="__NEXT_DATA__">{json_text}</script></html>'.encode("utf-8")
    
    # Track call count
    call_count = [0]
    
    def mock_get(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            # First call returns WAF challenge
            return SimpleNamespace(
                status_code=403,
                text='<html><body>AWS WAF Challenge</body></html>',
                content=b'<html><body>AWS WAF Challenge</body></html>',
                cookies={'aws-waf-token': 'test-token'}
            )
        else:
            # Second call (after solving challenge) returns actual data
            return SimpleNamespace(
                status_code=200,
                content=html,
                text=html.decode('utf-8')
            )
    
    return mock_get


def test_request_json_url_handles_waf_challenge(monkeypatch):
    """Test that request_json_url properly handles and solves WAF challenges"""
    mock_get = mock_get_with_waf_challenge_factory("sample_resource.json")
    monkeypatch.setattr(services.niquests, "get", mock_get)
    
    # Should detect WAF challenge, solve it, and retry successfully
    result = services.request_json_url("https://www.imdb.com/title/tt0133093/reference")
    
    # Verify we got valid data (not the challenge page)
    assert result is not None
    assert isinstance(result, dict)


def test_search_title_handles_waf_challenge(monkeypatch):
    """Test that search_title properly handles WAF challenges"""
    mock_get = mock_get_with_waf_challenge_factory("sample_search.json")
    monkeypatch.setattr(services.niquests, "get", mock_get)
    
    result = services.search_title("matrix")
    
    # Should have successfully solved the challenge and returned results
    assert result is not None
    assert result.titles[0].title == "The Matrix"


def test_get_movie_handles_waf_challenge(monkeypatch):
    """Test that get_movie properly handles WAF challenges"""
    mock_get = mock_get_with_waf_challenge_factory("sample_resource.json")
    monkeypatch.setattr(services.niquests, "get", mock_get)
    
    movie = services.get_movie("tt0133093")
    
    # Should have successfully solved the challenge and returned movie data
    assert movie is not None
    assert movie.title == "The Matrix"
    assert movie.duration == 136


def mock_post_with_waf_challenge():
    """Mock POST request that returns WAF challenge first, then success"""
    call_count = [0]
    
    def mock_post(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            # First call returns WAF challenge
            return SimpleNamespace(
                status_code=403,
                text='<html><body>AWS WAF Challenge for GraphQL</body></html>',
                content=b'<html><body>AWS WAF Challenge</body></html>',
                cookies={'aws-waf-token': 'graphql-token'}
            )
        else:
            # Second call returns success
            return SimpleNamespace(
                status_code=200,
                text='{"data": {"title": {"id": "tt0133093"}}}',
                json=lambda: {"data": {"title": {"id": "tt0133093"}}}
            )
    
    return mock_post


def test_method_name_handles_waf_challenge(monkeypatch):
    """Test that method_name (GraphQL) properly handles WAF challenges"""
    mock_post = mock_post_with_waf_challenge()
    
    # Use monkeypatch to set the post attribute on services.niquests
    monkeypatch.setattr('imdbinfo.services.niquests.post', mock_post, raising=False)
    
    headers = {"Content-Type": "application/json"}
    payload = {"query": "test query"}
    
    result = services.method_name(headers, "tt0133093", payload, "https://api.graphql.imdb.com/")
    
    # Should have successfully solved the challenge and returned data
    assert result is not None
    assert "data" in result
