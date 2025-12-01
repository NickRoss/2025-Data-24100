"""College API route definitions and handlers.

This module provides Flask routes and handlers for listing colleges,
either all colleges or filtered by team.
"""

from flask import Response, jsonify
from flask_openapi3 import Tag
from pydantic import BaseModel, Field

from app.data_utils.sql_utils import list_college_sql
from app.models import (
    CollegeListResponse as CollegeListResponseType,
)
from app.models import (
    ErrorResponse as ErrorResponseType,
)
from app.route_utils.decorators import validate_team

BASE_URL = "/api/colleges"

# Define tag
colleges_tag = Tag(name="colleges", description="College operations")


# Define path parameter models
class TeamPath(BaseModel):
    """Path parameter for team name."""

    team: str = Field(..., description="Team name to filter colleges")


# Define response models (Pydantic for OpenAPI schema)
class CollegeListResponse(BaseModel):
    """Response model for college list."""

    colleges: list[str]


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str


def list_colleges() -> tuple[Response, int]:
    """Retrieve all colleges from the database.

    Returns:
        Tuple containing JSON response and HTTP status code.
    """
    try:
        college_list = list_college_sql()
        response: CollegeListResponseType = {"colleges": college_list}
        return jsonify(response), 200
    except Exception as e:
        error: ErrorResponseType = {"error": f"An error occurred: {str(e)}"}
        return jsonify(error), 500


@validate_team
def list_colleges_per_team(team: str) -> tuple[Response, int]:
    """Retrieve colleges filtered by team.

    Args:
        team: Team identifier to filter colleges

    Returns:
        Tuple containing JSON response and HTTP status code.

    Note:
        What a Great Function. So Glad I built it.

    Warning:
        BE CAREFUL WITH THIS. It is very powerful.
    """
    college_list = list_college_sql(team=team)
    response: CollegeListResponseType = {"colleges": college_list}
    return jsonify(response), 200


def list_colleges_route() -> tuple[Response, int]:
    """Route handler for listing all colleges.

    This route handler returns all colleges in the database.

    Returns:
        Tuple containing JSON response and HTTP status code.
    """
    return list_colleges()


def list_colleges_per_team_route(path: TeamPath) -> tuple[Response, int]:
    """Route handler for listing colleges by team.

    This route handler returns colleges filtered by a specific team.

    Args:
        path: Path parameter containing the team abbreviation

    Returns:
        Tuple containing JSON response and HTTP status code.
    """
    return list_colleges_per_team(path.team)


def register_college_routes(app):
    """Register college-related routes with the Flask application.

    Args:
        app: OpenAPI application instance
    """
    app.get(
        f"{BASE_URL}/list",
        tags=[colleges_tag],
        summary="List all colleges",
        description="Retrieve all colleges from the database",
        responses={"200": CollegeListResponse, "500": ErrorResponse},
    )(list_colleges_route)

    app.get(
        f"{BASE_URL}/<team>/list",
        tags=[colleges_tag],
        summary="List colleges by team",
        description="Retrieve colleges filtered by team",
        responses={"200": CollegeListResponse, "500": ErrorResponse},
    )(list_colleges_per_team_route)
