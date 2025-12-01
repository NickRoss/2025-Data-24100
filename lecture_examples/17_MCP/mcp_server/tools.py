"""MCP tool definitions for Basketball API.

This module contains all the tool functions that interact with the Flask API.
"""

import os

import httpx
from fastmcp import FastMCP

from models import (
    AddPlayerResponse,
    AllPlayersResponse,
    DeletePlayerResponse,
    PlayerDict,
    PlayerInfo,
    TeamPlayersResponse,
)

# Flask API configuration
FLASK_API_URL = os.environ["FLASK_API_URL"]

# Create FastMCP instance
mcp = FastMCP("Basketball API Server")


@mcp.tool()
async def get_all_players() -> AllPlayersResponse:
    """Get a list of all basketball players in the database.

    Players are grouped by team.

    Returns:
        AllPlayersResponse: Dictionary with "players" key containing list of player dicts
            with "id" (int) and "player_name" (str) keys.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FLASK_API_URL}/api/players")
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_player_info(player_id: int) -> PlayerInfo:
    """Get detailed information about a specific player by their ID.

    Args:
        player_id: The unique ID of the player

    Returns:
        PlayerInfo: Player information including id, player_name,
            team_abbreviation, college, age, stats (pts, reb, ast), and
            other fields.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FLASK_API_URL}/api/players/{player_id}")
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_players_by_team(team: str) -> TeamPlayersResponse:
    """Get all players for a specific team.

    Args:
        team: The 3-letter team abbreviation (e.g., 'LAL', 'WAS', 'BOS')

    Returns:
        TeamPlayersResponse: Dictionary keyed by team abbreviation containing list of player
            dicts with "id" (int) and "player_name" (str) keys.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{FLASK_API_URL}/api/teams/players/{team}/list"
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def add_player(
    player_name: str, team: str, college: str = None
) -> AddPlayerResponse:
    """Add a new player to the database.

    Args:
        player_name: The name of the player
        team: The 3-letter team abbreviation (e.g., 'LAL', 'WAS', 'BOS')
        college: The college the player attended (optional)

    Returns:
        AddPlayerResponse: Dictionary with "message" (str) and "player"
            (dict with "name", "team", "college" keys) fields.
    """
    async with httpx.AsyncClient() as client:
        payload = {
            "player_name": player_name,
            "team": team,
            "college": college,
        }
        response = await client.post(
            f"{FLASK_API_URL}/api/players", json=payload
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def delete_player(player_id: int) -> DeletePlayerResponse:
    """Delete a player from the database by their ID.

    Args:
        player_id: The unique ID of the player to delete

    Returns:
        DeletePlayerResponse: Dictionary with "message" (str) key.

    Note:
        Use get_player_info first to find the player ID.
    """
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{FLASK_API_URL}/api/players/{player_id}"
        )
        response.raise_for_status()
        return {"message": f"Player {player_id} deleted successfully"}
