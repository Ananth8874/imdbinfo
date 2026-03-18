"""User-Agent generation and selection utilities."""

import random
from typing import List, Optional

_WINDOWS_PLATFORMS = [
    "Windows NT 10.0; Win64; x64",
    "Windows NT 10.0; WOW64",
    "Windows NT 6.1; Win64; x64",
]

_MAC_PLATFORMS = [
    "Macintosh; Intel Mac OS X 10_15_7",
    "Macintosh; Intel Mac OS X 11_7_10",
    "Macintosh; Intel Mac OS X 12_7_6",
]

_LINUX_PLATFORMS = [
    "X11; Linux x86_64",
    "X11; Ubuntu; Linux x86_64",
]


def _build_chrome_user_agent() -> str:
    major = random.randint(128, 146)
    build = random.randint(0, 9999)
    patch = random.randint(0, 199)
    platform = random.choice(_WINDOWS_PLATFORMS + _MAC_PLATFORMS + _LINUX_PLATFORMS)
    return (
        "Mozilla/5.0 ({platform}) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/{major}.0.{build}.{patch} Safari/537.36"
    ).format(platform=platform, major=major, build=build, patch=patch)


def _build_edge_user_agent() -> str:
    major = random.randint(126, 144)
    build = random.randint(0, 9999)
    patch = random.randint(0, 199)
    platform = random.choice(_WINDOWS_PLATFORMS)
    return (
        "Mozilla/5.0 ({platform}) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/{major}.0.{build}.{patch} Safari/537.36 "
        "Edg/{major}.0.{build}.{patch}"
    ).format(platform=platform, major=major, build=build, patch=patch)


def _build_firefox_user_agent() -> str:
    major = random.randint(120, 136)
    platform = random.choice(_WINDOWS_PLATFORMS + _MAC_PLATFORMS + _LINUX_PLATFORMS)
    return (
        "Mozilla/5.0 ({platform}; rv:{major}.0) "
        "Gecko/20100101 Firefox/{major}.0"
    ).format(platform=platform, major=major)


def generate_user_agent_item() -> str:
    """Create a fresh, randomized user-agent string."""
    builder = random.choice(
        [_build_chrome_user_agent, _build_edge_user_agent, _build_firefox_user_agent]
    )
    return builder()


def generate_user_agents_list(size: int = 8) -> List[str]:
    """Create a list of randomized user-agent strings."""
    if size < 1:
        raise ValueError("size must be greater than 0")
    return [generate_user_agent_item() for _ in range(size)]


def get_random_user_agent(user_agents_list: Optional[List[str]] = None) -> str:
    """Pick from a provided list or generate a fresh value on demand."""
    if user_agents_list:
        return random.choice(user_agents_list)
    return generate_user_agent_item()

