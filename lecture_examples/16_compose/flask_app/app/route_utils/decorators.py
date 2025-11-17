"""Decorator functions for request validation, logging and timing."""

import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from flask import Response, jsonify, request

from app.data_utils.sql_utils import all_teams_sql
from app.logger_utils.custom_logger import custom_logger

# Type for decorated functions
F = TypeVar("F", bound=Callable[..., Any])
ApiResponse = tuple[Response | dict, int]


def validate_team(f: F) -> F:
    """Validates team exists, returns 404 if not found.

    Args:
        f: Function to decorate

    Returns:
        Decorated function that validates team parameter
    """

    @wraps(f)
    def decorated_function(
        team: str, *args: Any, **kwargs: Any
    ) -> ApiResponse:
        all_teams = all_teams_sql()
        if team not in all_teams:
            return jsonify({"Error": f"Team {team} does not exist"}), 404
        return f(team, *args, **kwargs)

    return decorated_function  # type: ignore


def log_request_response(f: F) -> F:
    """Logs incoming requests and outgoing responses.

    Args:
        f: Function to decorate

    Returns:
        Decorated function that logs request/response
    """

    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> ApiResponse:
        custom_logger.debug(
            f"Request received: {request.method} {request.path}"
        )
        response = f(*args, **kwargs)
        custom_logger.debug(f"Response: {response[1]} - {request.path}")
        return response

    return decorated_function  # type: ignore


def log_request_response_time(f: F) -> F:
    """Logs request/response with execution time in milliseconds.

    Args:
        f: Function to decorate

    Returns:
        Decorated function that logs timing info
    """

    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> ApiResponse:
        start_time = time.time()
        custom_logger.info(
            f"Request received: {request.method} {request.path}"
        )
        response = f(*args, **kwargs)
        execution_time = (time.time() - start_time) * 1000
        custom_logger.info(
            f"Response: {response[1]} - {request.path} "
            f"- Execution time: {execution_time:.2f}ms"
        )
        return response

    return decorated_function  # type: ignore
