import sys
from types import SimpleNamespace

# Provide a minimal stub for the 'niquests' module so that the package can be imported
# in environments where the real dependency is unavailable.
sys.modules.setdefault("niquests", SimpleNamespace(get=lambda *args, **kwargs: None))

# Provide a minimal stub for the 'curl_cffi' module so that the package can be imported
# in environments where the real dependency is unavailable.
if "curl_cffi" not in sys.modules:
    mock_cffi_requests = SimpleNamespace(get=lambda *args, **kwargs: None)
    sys.modules["curl_cffi"] = SimpleNamespace(requests=mock_cffi_requests)
    sys.modules["curl_cffi.requests"] = mock_cffi_requests
