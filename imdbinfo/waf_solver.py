# MIT License
# Copyright (c) 2025 tveronesi+imdbinfo@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
AWS WAF Solver Module

This module provides functionality to detect and solve AWS WAF challenges
that may be encountered when making requests to IMDb.
"""

import re
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def is_waf_challenge(response: Any) -> bool:
    """
    Detect if the response contains an AWS WAF challenge.
    
    AWS WAF challenges typically contain specific patterns in the HTML response,
    such as challenge scripts or specific meta tags.
    
    Args:
        response: The HTTP response object to check
        
    Returns:
        True if a WAF challenge is detected, False otherwise
    """
    if not hasattr(response, 'text') or not response.text:
        return False
    
    content = response.text.lower()
    
    # Common AWS WAF challenge indicators
    waf_patterns = [
        'aws-waf',
        'awswaf',
        'challenge.aws',
        'aws waf captcha',
        'aws waf challenge',
        'x-amzn-waf-action',
    ]
    
    for pattern in waf_patterns:
        if pattern in content:
            logger.debug(f"AWS WAF challenge detected: pattern '{pattern}' found in response")
            return True
    
    return False


def extract_challenge_script(html_content: str) -> Optional[str]:
    """
    Extract the AWS WAF challenge JavaScript code from the HTML response.
    
    Note: This function is used for detection purposes only, not for security filtering.
    The actual HTML parsing is done by lxml which properly handles malformed HTML.
    
    Args:
        html_content: The HTML content containing the challenge
        
    Returns:
        The extracted JavaScript code, or None if not found
    """
    # Use lxml for robust HTML parsing instead of regex
    try:
        from lxml import html as html_parser
        tree = html_parser.fromstring(html_content)
        scripts = tree.xpath('//script/text()')
        
        for script in scripts:
            # AWS WAF challenges typically contain certain keywords
            if isinstance(script, str) and ('challenge' in script.lower() or 'captcha' in script.lower()):
                logger.debug("Found potential AWS WAF challenge script")
                return script
    except Exception as e:
        logger.debug(f"Failed to parse HTML with lxml: {e}")
        # Fallback: return None if parsing fails
        return None
    
    logger.debug("No AWS WAF challenge script found")
    return None


def solve_waf_challenge(
    response: Any,
    url: str,
    headers: Optional[Dict[str, str]] = None
) -> Optional[Dict[str, str]]:
    """
    Solve the AWS WAF challenge and return the cookies needed to bypass it.
    
    This is a placeholder implementation. Real AWS WAF challenges may require
    more sophisticated solutions, potentially including:
    - JavaScript execution using js2py or similar
    - Browser automation using Selenium or Playwright
    - Specific cookie/token generation algorithms
    
    Args:
        response: The HTTP response containing the challenge
        url: The original URL that was requested
        headers: Optional headers that may be used in future implementations
                for more sophisticated challenge solving
        
    Returns:
        A dictionary of cookies to use in subsequent requests, or None if solving failed
    """
    logger.info(f"Attempting to solve AWS WAF challenge for {url}")
    
    if not hasattr(response, 'text'):
        logger.warning("Response has no text content, cannot solve challenge")
        return None
    
    # Try to extract any cookies from the response
    cookies = {}
    if hasattr(response, 'cookies'):
        for cookie_name, cookie_value in response.cookies.items():
            cookies[cookie_name] = cookie_value
            logger.debug(f"Extracted cookie: {cookie_name}")
    
    # For now, return any cookies we found
    # A more sophisticated implementation would:
    # 1. Execute the JavaScript challenge code
    # 2. Generate the required tokens/cookies
    # 3. Return those for use in the retry request
    
    if cookies:
        logger.info(f"Extracted {len(cookies)} cookies from AWS WAF challenge response")
        return cookies
    
    logger.warning("No cookies could be extracted from AWS WAF challenge")
    return None
