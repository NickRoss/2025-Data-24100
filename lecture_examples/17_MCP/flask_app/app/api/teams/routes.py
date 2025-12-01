"""Team API route definitions and handlers.

This module provides Flask routes and handlers for team-related operations,
specifically listing players by team.
"""

from flask import Response, jsonify
from flask_openapi3 import Tag
from pydantic import BaseModel, ConfigDict, Field

from app.data_utils.sql_utils import list_players_per_team_sql
from app.models import PlayerDict
from app.route_utils.decorators import (
    log_request_response,
    log_request_response_time,
    validate_team,
)

BASE_URL = "/api/teams"

# Define tag
teams_tag = Tag(name="teams", description="Team operations")


# Define path parameter models
class TeamPath(BaseModel):
    """Path parameter for team name."""

    team: str = Field(..., description="Team name to filter players")


# Define response models (Pydantic for OpenAPI schema)
class TeamPlayersResponse(BaseModel):
    """Response model for team players."""

    model_config = ConfigDict(extra="allow")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str


@validate_team
@log_request_response
@log_request_response_time
def list_players_per_team(team: str) -> tuple[Response, int]:
    """List all players for a specific team.

    Args:
        team: Team identifier to filter players

    Returns:
        Tuple containing JSON response and HTTP status code.
    """
    list_of_players: list[PlayerDict] = list_players_per_team_sql(team)
    to_return: dict[str, list[PlayerDict]] = {team: list_of_players}
    return jsonify(to_return), 200


def list_players_per_team_route(path: TeamPath) -> tuple[Response, int]:
    """Route handler for listing players by team.

    This is the Flask-OpenAPI3 route handler that gets registered with the app.
    It extracts the team from the path parameter and calls the business logic.

    Args:
        path: Path parameter containing the team abbreviation

    Returns:
        Tuple containing JSON response and HTTP status code.
    """
    return list_players_per_team(path.team)


def register_team_routes(app):
    """Register team-related routes with the Flask application.

    Args:
        app: OpenAPI application instance
    """
    app.get(
        f"{BASE_URL}/players/<team>/list",
        tags=[teams_tag],
        summary="List players by team",
        description="List all players for a specific team",
        responses={"200": TeamPlayersResponse, "500": ErrorResponse},
    )(list_players_per_team_route)
