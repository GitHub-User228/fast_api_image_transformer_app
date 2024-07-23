from fastapi import Request
from fastapi_limiter.depends import RateLimiter

from fast_api_project.settings import (
    get_global_request_rate_limit_settings,
    get_ip_request_rate_limit_settings,
)
from fast_api_project.utils.callbacks import global_callback, per_ip_callback


async def get_ip_key(request: Request) -> str:
    """
    Extracts and returns the client's IP address from the FastAPI
    request.

    Parameters:
        request (Request):
            The FastAPI request object containing information about
            the incoming request.

    Returns:
        str:
            The client's IP address as a string.
    """
    try:
        return request.client.host
    except AttributeError:
        return "unknown"


# Rate limiter for global requests
global_limiter = RateLimiter(
    **dict(get_global_request_rate_limit_settings()),
    callback=global_callback,
)

# Rate limiter for requests per IP address
ip_limiter = RateLimiter(
    **dict(get_ip_request_rate_limit_settings()),
    identifier=get_ip_key,
    callback=per_ip_callback,
)
