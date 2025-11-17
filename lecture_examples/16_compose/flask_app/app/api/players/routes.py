"""Player API route definitions and handlers.

This module provides Flask routes and handlers for managing players,
including listing, adding, deleting, and retrieving player information.
"""

from typing import Any

from flask import jsonify
from flask_openapi3 import Tag
from pydantic import BaseModel, ConfigDict, Field

from app.data_utils.sql_utils import (
    add_player,
    delete_player,
    list_players_per_team_sql,
    player_info_sql,
)

BASE_URL = "/api/players"

# Define tag
players_tag = Tag(name="players", description="Player operations")


class PlayerInput(BaseModel):
    """Player input model for adding a new player."""

    player_name: str = Field(..., description="Name of the player")
    team: str = Field(..., description="Team name")
    college: str | None = Field(None, description="College name")


class PlayerIdPath(BaseModel):
    """Path parameter for player ID."""

    player_id: int = Field(..., description="The ID of the player")


class PlayerListResponse(BaseModel):
    """Response model for player list."""

    players: list[dict[str, Any]]


class PlayerInfo(BaseModel):
    """Player information model."""

    name: str
    team: str
    college: str | None


class PlayerInfoResponse(BaseModel):
    """Response model for player info endpoint."""

    model_config = ConfigDict(extra="allow")


class PlayerAddedResponse(BaseModel):
    """Response model for adding a player."""

    message: str
    player: PlayerInfo


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str


def register_player_routes(app):
    """Register player-related routes with the Flask application.

    Args:
        app: OpenAPI application instance
    """

    @app.get(
        f"{BASE_URL}",
        tags=[players_tag],
        summary="List all players",
        description="Retrieve all players grouped by team",
        responses={"200": PlayerListResponse, "500": ErrorResponse},
    )
    def list_players():
        """Retrieve all players grouped by team."""
        try:
            players_list = list_players_per_team_sql()
            return jsonify({"players": players_list}), 200
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    @app.post(
        f"{BASE_URL}",
        tags=[players_tag],
        summary="Add a new player",
        description="Add a new player to the database",
        responses={"201": PlayerAddedResponse, "500": ErrorResponse},
    )
    def add_player_route(body: PlayerInput):
        """Add a new player to the database."""
        try:
            data = {
                "player_name": body.player_name,
                "team": body.team,
                "college": body.college,
            }
            add_player(data)
            return jsonify(
                {
                    "message": (
                        f"Successfully added player: {body.player_name}"
                    ),
                    "player": {
                        "name": body.player_name,
                        "team": body.team,
                        "college": body.college,
                    },
                }
            ), 201
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    @app.delete(
        f"{BASE_URL}/<int:player_id>",
        tags=[players_tag],
        summary="Delete a player",
        description="Delete a player by their ID",
        responses={"204": None, "500": ErrorResponse},
    )
    def delete_player_route(path: PlayerIdPath):
        """Delete a player by their ID."""
        try:
            delete_player(path.player_id)
            return "", 204
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    @app.get(
        f"{BASE_URL}/<int:player_id>",
        tags=[players_tag],
        summary="Get player information",
        description="Get detailed information for a specific player",
        responses={"200": PlayerInfoResponse, "500": ErrorResponse},
    )
    def get_player_info(path: PlayerIdPath):
        """Get detailed information for a specific player."""
        try:
            player_info = player_info_sql(path.player_id)
            if len(player_info) != 1:
                raise Exception("Player ID Unknown")
            return jsonify(player_info[0]), 200
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
