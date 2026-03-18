"""
Example: User-Agent behaviour

User-Agent strings are managed internally by the imdbinfo engine.
A fresh, randomised UA is generated for every request — no external
override is needed or supported.

The engine (imdbinfo.user_agents_list) can still be used standalone
if you need to inspect or generate UA strings for other purposes.
"""

from imdbinfo import get_movie
from imdbinfo.user_agents_list import (
    generate_user_agent_item,
    generate_user_agents_list,
)

# ------------------------------------------------------------------
# 1. Inspect what a generated UA looks like
# ------------------------------------------------------------------
print("Sample generated User-Agent:")
print(f"  {generate_user_agent_item()}\n")

# ------------------------------------------------------------------
# 2. Generate a batch for inspection
# ------------------------------------------------------------------
sample_list = generate_user_agents_list(size=4)
print("Sample batch (4 items):")
for ua in sample_list:
    print(f"  {ua}")
print()

# ------------------------------------------------------------------
# 3. Every real request automatically uses a fresh random UA —
#    no configuration required.
# ------------------------------------------------------------------
try:
    movie = get_movie("tt0133093")  # The Matrix
    print(f"Fetched movie : {movie.title} ({movie.year})")
    print(f"Rating        : {movie.rating}")
except Exception as e:
    print(f"Error: {e}")
