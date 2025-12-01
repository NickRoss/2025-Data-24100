"""Type aliases for Basketball API MCP Server.

This module contains type aliases used for structured responses
from the MCP tools. All responses are plain dictionaries.
"""

from typing import Any

# Type aliases for better readability
PlayerDict = dict[str, int | str]
PlayerInfo = dict[str, Any]  # Player information with all fields
AllPlayersResponse = dict[str, list[PlayerDict]]  # {"players": [...]}
TeamPlayersResponse = dict[
    str, list[PlayerDict]
]  # {"LAL": [...], "BOS": [...]}
PlayerAddedPlayer = dict[str, str | None]  # name, team, college
AddPlayerResponse = dict[str, Any]  # message, player
DeletePlayerResponse = dict[str, str]  # message
