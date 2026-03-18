"""
Example: Using a custom User-Agent

This example demonstrates how to override the default User-Agent
used for HTTP requests to IMDb.

The User-Agent engine lives in imdbinfo.user_agents_list and generates
randomized UA strings by default. You can replace services.USER_AGENTS_LIST
at any time to force specific values for all subsequent requests.
"""

import imdbinfo.services as services
from imdbinfo import get_movie
from imdbinfo.user_agents_list import (
    generate_user_agent_item,
    generate_user_agents_list,
    get_random_user_agent,
)

# ------------------------------------------------------------------
# 1. Inspect the default list (8 freshly generated UA strings)
# ------------------------------------------------------------------
print("Default User-Agent List (first item):")
print(f"  {services.USER_AGENTS_LIST[0]}")
print(f"  ... ({len(services.USER_AGENTS_LIST)} items total)\n")

# ------------------------------------------------------------------
# 2. Generate a single random UA on demand
# ------------------------------------------------------------------
fresh_ua = generate_user_agent_item()
print(f"Freshly generated UA: {fresh_ua}\n")

# ------------------------------------------------------------------
# 3. Override the list — all subsequent requests will pick from this
#    Must assign to services.USER_AGENTS_LIST (not a local variable)
# ------------------------------------------------------------------
services.USER_AGENTS_LIST = [
    "MyCustomApp/1.0 (Contact: myemail@example.com)",
    "AnotherUserAgent/2.0",
]
print(f"Custom User-Agent List: {services.USER_AGENTS_LIST}\n")

# ------------------------------------------------------------------
# 4. Pick a random UA from the overridden list
# ------------------------------------------------------------------
chosen = get_random_user_agent(services.USER_AGENTS_LIST)
print(f"Chosen UA for next request: {chosen}\n")

# ------------------------------------------------------------------
# 5. Make a real request using the custom UA list
# ------------------------------------------------------------------
try:
    services.get_movie.cache_clear()
    movie = get_movie("tt0133093")  # The Matrix
    print(f"Fetched movie: {movie.title} ({movie.year})")
    print(f"Rating: {movie.rating}")
except Exception as e:
    print(f"Error: {e}")

# ------------------------------------------------------------------
# 6. Restore default (generate a fresh list)
# ------------------------------------------------------------------
services.USER_AGENTS_LIST = generate_user_agents_list(size=8)
print(f"\nRestored default UA list ({len(services.USER_AGENTS_LIST)} items).")
