import sys
import pytest
from types import SimpleNamespace

# Provide a minimal stub for the 'niquests' module so that the package can be imported
# in environments where the real dependency is unavailable.
sys.modules.setdefault("niquests", SimpleNamespace(get=lambda *args, **kwargs: None))


@pytest.fixture(autouse=True)
def reset_waf_state():
    """Reset global WAF state before each test for predictable, network-free behavior."""
    from imdbinfo import services
    original = services.WAF_ON
    services.WAF_ON = False
    yield
    services.WAF_ON = original
