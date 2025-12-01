"""MCP tool definitions for Basketball API.

This module contains all the tool functions that interact with the Flask API.
"""

import os

import httpx
from fastmcp import FastMCP

# Flask API configuration
FLASK_API_URL = os.getenv("FLASK_API_URL", "http://flask-app:5000")

# Create FastMCP instance
mcp = FastMCP("Basketball API Server")


@mcp.tool()
async def get_all_players() -> str:
    """Get a list of all basketball players in the database.

    Players are grouped by team.

    Returns:
        str: Player names, IDs, and team information.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FLASK_API_URL}/api/players")
        response.raise_for_status()
        result = response.json()
        return str(result)


@mcp.tool()
async def get_player_info(player_id: int) -> str:
    """Get detailed information about a specific player by their ID.

    Args:
        player_id: The unique ID of the player

    Returns:
        str: Player name, team, college, and statistics.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FLASK_API_URL}/api/players/{player_id}")
        response.raise_for_status()
        result = response.json()
        return str(result)


@mcp.tool()
async def get_players_by_team(team: str) -> str:
    """Get all players for a specific team.

    Args:
        team: The 3-letter team abbreviation (e.g., 'LAL', 'WAS', 'BOS')

    Returns:
        str: A list of all players on that team.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{FLASK_API_URL}/api/teams/players/{team}/list"
        )
        response.raise_for_status()
        result = response.json()
        return str(result)


@mcp.tool()
async def add_player(player_name: str, team: str, college: str = None) -> str:
    """Add a new player to the database.

    Args:
        player_name: The name of the player
        team: The 3-letter team abbreviation (e.g., 'LAL', 'WAS', 'BOS')
        college: The college the player attended (optional)

    Returns:
        str: Success message and player information.
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
        result = response.json()
        return str(result)


@mcp.tool()
async def delete_player(player_id: int) -> str:
    """Delete a player from the database by their ID.

    Args:
        player_id: The unique ID of the player to delete

    Returns:
        str: Success message.

    Note:
        Use get_player_info first to find the player ID.
    """
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{FLASK_API_URL}/api/players/{player_id}"
        )
        response.raise_for_status()
        result = {"message": f"Player {player_id} deleted successfully"}
        return str(result)


@mcp.tool()
async def get_players_by_college(college: str) -> str:
    """Get all players who attended a specific college.

    Args:
        college: The college name (e.g., 'Duke', 'University of Kentucky')

    Returns:
        str: Player information grouped by college.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{FLASK_API_URL}/api/colleges/{college}/players"
        )
        response.raise_for_status()
        result = response.json()
        return str(result)
