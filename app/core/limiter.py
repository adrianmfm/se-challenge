from slowapi import Limiter
from slowapi.util import get_remote_address

# Global rate limiter instance, keyed by client IP address.
# Default limit applies to any route that does not specify its own.
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
