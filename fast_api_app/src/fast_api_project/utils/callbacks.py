from fastapi import Request, Response, HTTPException

from fast_api_project import logger
from fast_api_project.utils.common import calculate_expire_time


async def global_callback(
    request: Request, response: Response, pexpire: int
) -> None:
    """
    Logs a warning message and raises an HTTP 429 Too Many Requests
    exception with the provided message and a Retry-After header set
    to the specified expire time.

    Args:
        request (Request):
            The incoming request object.
        response (Response):
            The outgoing response object.
        pexpire (int):
            The number of seconds the client should wait before retrying
            the request.
    """
    expire = calculate_expire_time(pexpire)
    message = f"Too Many Overall Requests. Retry after {expire} seconds."
    logger.warning(message)
    raise HTTPException(
        status_code=429,
        detail=message,
        headers={"Retry-After": str(expire)},
    )


async def per_ip_callback(
    request: Request, response: Response, pexpire: int
) -> None:
    """
    Logs a warning message and raises an HTTP 429 Too Many Requests
    exception with the provided message and a Retry-After header set
    to the specified expire time for requests from a specific IP address.

    Args:
        request (Request):
            The incoming request object.
        response (Response):
            The outgoing response object.
        pexpire (int):
            The number of seconds the client should wait before retrying
            the request.
    """
    expire = calculate_expire_time(pexpire)
    message = (
        f"Too Many Requests from your IP. " f"Retry after {expire} seconds."
    )
    logger.warning(message)
    raise HTTPException(
        status_code=429,
        detail=message,
        headers={"Retry-After": str(expire)},
    )
