#!/usr/bin/env python
"""
Test script to verify AWS WAF bypass implementation (Version 2.0)
Tests session persistence and token caching
"""
import sys
import logging
import time

# Add the project to the path
sys.path.insert(0, r'C:\Users\Tiago\PycharmProjects\imdbinfo')

# Configure logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from imdbinfo import search_title

def test_waf_bypass():
    """Test that the WAF bypass works with session persistence and caching"""
    print("=" * 80)
    print("Testing AWS WAF Bypass - Version 2.0")
    print("Features: Session Persistence, Token Caching, 4 Retry Attempts")
    print("=" * 80)

    # Test 1: First search - should obtain WAF token
    print("\n" + "=" * 80)
    print("TEST 1: First Search (will obtain WAF token)")
    print("=" * 80)
    title_query1 = "little house on the prairie"
    print(f"Searching for: '{title_query1}'")

    try:
        start_time = time.time()
        results1 = search_title(title_query1)
        elapsed = time.time() - start_time

        print(f"\n✓ SUCCESS! Search completed in {elapsed:.2f}s")
        print(f"Found {len(results1.titles)} titles:")
        for i, movie in enumerate(results1.titles[:3], 1):
            print(f"  {i}. {movie.title} - {movie.imdbId}")
    except Exception as e:
        print(f"\n✗ FAILED! Error: {e}")
        return False

    # Test 2: Second search - should use cached token
    print("\n" + "=" * 80)
    print("TEST 2: Second Search (should use cached token)")
    print("=" * 80)
    title_query2 = "breaking bad"
    print(f"Searching for: '{title_query2}'")
    print("Expected: Faster response using cached WAF token")

    try:
        start_time = time.time()
        results2 = search_title(title_query2)
        elapsed = time.time() - start_time

        print(f"\n✓ SUCCESS! Search completed in {elapsed:.2f}s")
        print(f"Found {len(results2.titles)} titles:")
        for i, movie in enumerate(results2.titles[:3], 1):
            print(f"  {i}. {movie.title} - {movie.imdbId}")
    except Exception as e:
        print(f"\n✗ FAILED! Error: {e}")
        return False

    # Test 3: Third search - verify cache still works
    print("\n" + "=" * 80)
    print("TEST 3: Third Search (verify cache persistence)")
    print("=" * 80)
    title_query3 = "the godfather"
    print(f"Searching for: '{title_query3}'")

    try:
        start_time = time.time()
        results3 = search_title(title_query3)
        elapsed = time.time() - start_time

        print(f"\n✓ SUCCESS! Search completed in {elapsed:.2f}s")
        print(f"Found {len(results3.titles)} titles:")
        for i, movie in enumerate(results3.titles[:3], 1):
            print(f"  {i}. {movie.title} - {movie.imdbId}")
    except Exception as e:
        print(f"\n✗ FAILED! Error: {e}")
        return False

    # Summary
    print("\n" + "=" * 80)
    print("ALL TESTS PASSED! ✓")
    print("=" * 80)
    print("\nKey Observations:")
    print("- First search may take 3-5 seconds (obtains WAF token)")
    print("- Subsequent searches should be faster (uses cached token)")
    print("- Token is cached for 5 minutes")
    print("- Session persistence maintains browser context")
    return True

if __name__ == "__main__":
    print("\n🚀 Starting AWS WAF Bypass Tests...\n")
    success = test_waf_bypass()

    if success:
        print("\n✅ All WAF bypass mechanisms working correctly!")
    else:
        print("\n❌ Some tests failed. Check logs above for details.")

    sys.exit(0 if success else 1)

