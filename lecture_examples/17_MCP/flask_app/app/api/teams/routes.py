"""Team API route definitions and handlers.

This module provides Flask routes and handlers for team-related operations,
specifically listing players by team.
"""

from flask import jsonify
from flask_openapi3 import Tag
from pydantic import BaseModel, ConfigDict, Field

from app.data_utils.sql_utils import list_players_per_team_sql
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


# Define response models
class TeamPlayersResponse(BaseModel):
    """Response model for team players."""

    model_config = ConfigDict(extra="allow")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str


@validate_team
@log_request_response
@log_request_response_time
def list_players_per_team(team):
    """List all players for a specific team.

    Args:
        team (str): Team identifier to filter players

    Returns:
        tuple: JSON response containing team's players and HTTP status code
    """
    list_of_players = list_players_per_team_sql(team)
    to_return = {team: list_of_players}
    return jsonify(to_return), 200


def register_team_routes(app):
    """Register team-related routes with the Flask application.

    Args:
        app: OpenAPI application instance
    """

    @app.get(
        f"{BASE_URL}/players/<team>/list",
        tags=[teams_tag],
        summary="List players by team",
        description="List all players for a specific team",
        responses={"200": TeamPlayersResponse, "500": ErrorResponse},
    )
    def list_players_per_team_route(path: TeamPath):
        """Route handler for listing players by team."""
        return list_players_per_team(path.team)
