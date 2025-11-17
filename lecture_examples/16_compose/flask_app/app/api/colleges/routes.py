"""College API route definitions and handlers.

This module provides Flask routes and handlers for listing colleges,
either all colleges or filtered by team.
"""

from flask import jsonify
from flask_openapi3 import Tag
from pydantic import BaseModel, Field

from app.data_utils.sql_utils import list_college_sql
from app.route_utils.decorators import validate_team

BASE_URL = "/api/colleges"

# Define tag
colleges_tag = Tag(name="colleges", description="College operations")


# Define path parameter models
class TeamPath(BaseModel):
    """Path parameter for team name."""

    team: str = Field(..., description="Team name to filter colleges")


# Define response models
class CollegeListResponse(BaseModel):
    """Response model for college list."""

    colleges: list[str]


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str


def list_colleges():
    """Retrieve all colleges from the database.

    Returns:
        tuple: JSON response with college list and HTTP status code
    """
    try:
        college_list = list_college_sql()
        return jsonify({"colleges": college_list}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@validate_team
def list_colleges_per_team(team):
    """Retrieve colleges filtered by team. tre

    Args:
        team (str): Team identifier to filter colleges

    Returns:
        tuple: JSON response with filtered college list and HTTP status code

    Note:
        What a Great Function. So Glad I built it.

    Warning:
        BE CAREFUL WITH THIS. It is very powerful.

    """
    college_list = list_college_sql(team=team)
    return jsonify({"colleges": college_list}), 200


def register_college_routes(app):
    """Register college-related routes with the Flask application.

    Args:
        app: OpenAPI application instance
    """

    @app.get(
        f"{BASE_URL}/list",
        tags=[colleges_tag],
        summary="List all colleges",
        description="Retrieve all colleges from the database",
        responses={"200": CollegeListResponse, "500": ErrorResponse},
    )
    def list_colleges_route():
        """Route handler for listing all colleges."""
        return list_colleges()

    @app.get(
        f"{BASE_URL}/<team>/list",
        tags=[colleges_tag],
        summary="List colleges by team",
        description="Retrieve colleges filtered by team",
        responses={"200": CollegeListResponse, "500": ErrorResponse},
    )
    def list_colleges_per_team_route(path: TeamPath):
        """Route handler for listing colleges by team."""
        return list_colleges_per_team(path.team)
