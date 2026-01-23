import pytest
from types import SimpleNamespace
from imdbinfo.waf_solver import is_waf_challenge, extract_challenge_script, solve_waf_challenge


def test_is_waf_challenge_detects_aws_waf():
    """Test that AWS WAF challenges are correctly detected"""
    # Mock response with AWS WAF challenge
    response = SimpleNamespace(
        text='<html><body>AWS WAF Challenge</body></html>',
        status_code=403
    )
    assert is_waf_challenge(response) is True


def test_is_waf_challenge_detects_awswaf():
    """Test that awswaf pattern is detected"""
    response = SimpleNamespace(
        text='<html><body>awswaf challenge page</body></html>',
        status_code=403
    )
    assert is_waf_challenge(response) is True


def test_is_waf_challenge_returns_false_for_normal_response():
    """Test that normal responses are not flagged as challenges"""
    response = SimpleNamespace(
        text='<html><body>Normal content</body></html>',
        status_code=200
    )
    assert is_waf_challenge(response) is False


def test_is_waf_challenge_handles_no_text():
    """Test that responses without text attribute don't crash"""
    response = SimpleNamespace(status_code=200)
    assert is_waf_challenge(response) is False


def test_extract_challenge_script_finds_challenge():
    """Test that challenge scripts can be extracted"""
    html = '''
    <html>
    <body>
        <script>console.log("normal script");</script>
        <script>
            // AWS WAF Challenge
            var challenge = "test";
        </script>
    </body>
    </html>
    '''
    script = extract_challenge_script(html)
    assert script is not None
    assert 'challenge' in script.lower()


def test_extract_challenge_script_returns_none_when_not_found():
    """Test that None is returned when no challenge script is found"""
    html = '<html><body><script>console.log("normal");</script></body></html>'
    script = extract_challenge_script(html)
    assert script is None


def test_solve_waf_challenge_extracts_cookies():
    """Test that cookies are extracted from challenge responses"""
    # Create a mock response with cookies
    mock_cookies = {'aws-waf-token': 'test-token-123'}
    response = SimpleNamespace(
        text='<html><body><script>var challenge = "test";</script></body></html>',
        status_code=403,
        cookies=mock_cookies
    )
    
    cookies = solve_waf_challenge(response, 'https://example.com', {})
    assert cookies is not None
    assert 'aws-waf-token' in cookies
    assert cookies['aws-waf-token'] == 'test-token-123'


def test_solve_waf_challenge_handles_no_cookies():
    """Test that the solver handles responses without cookies gracefully"""
    response = SimpleNamespace(
        text='<html><body>Challenge without cookies</body></html>',
        status_code=403,
        cookies={}
    )
    
    cookies = solve_waf_challenge(response, 'https://example.com', {})
    # Should return None when no cookies are found
    assert cookies is None


def test_solve_waf_challenge_handles_no_text():
    """Test that the solver handles responses without text attribute"""
    response = SimpleNamespace(
        status_code=403,
        cookies={'test': 'value'}
    )
    
    cookies = solve_waf_challenge(response, 'https://example.com', {})
    assert cookies is None
