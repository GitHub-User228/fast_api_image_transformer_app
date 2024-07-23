from fastapi import Request, Response, HTTPException

from fast_api_project import logger
from fast_api_project.utils.common import calculate_expire_time


def log_and_raise_http_exception(message: str, expire: int) -> None:
    """
    Logs a warning message and raises an HTTP 429 Too Many Requests
    exception with the provided message and a Retry-After header set
    to the specified expire time for overall requests.

    Args:
        message (str):
            The error message to log and include in the exception.
        expire (int):
            The number of seconds the client should wait before
            retrying the request.
    """
    logger.warning(message)
    raise HTTPException(
        status_code=429,
        detail=message,
        headers={"Retry-After": str(expire)},
    )


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
    try:
        expire = calculate_expire_time(pexpire)
        message = f"ERROR 429. Too Many Overall Requests. Retry after {expire} seconds."
        log_and_raise_http_exception(message, expire)
    except Exception as e:
        message = f"An error occurred in global_callback"
        logger.error(f"{message}: {str(e)}")
        raise HTTPException(status_code=500, detail=message)


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
    try:
        expire = calculate_expire_time(pexpire)
        message = (
            f"ERROR 429. Too Many Requests from your IP. "
            f"Retry after {expire} seconds."
        )
        log_and_raise_http_exception(message, expire)
    except Exception as e:
        message = f"An error occurred in per_ip_callback"
        logger.error(f"{message}: {str(e)}")
        raise HTTPException(status_code=500, detail=message)
