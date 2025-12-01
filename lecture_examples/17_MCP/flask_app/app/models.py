"""Type aliases for Basketball API Flask application.

This module contains type aliases used for structured responses
from the Flask API routes. All responses are plain dictionaries.
"""

from typing import Any

# Type aliases
PlayerDict = dict[str, int | str]
PlayerInfo = dict[str, Any]  # Player information with all fields
AllPlayersResponse = dict[str, list[PlayerDict]]  # players key
PlayerAddedPlayer = dict[str, str | None]  # name, team, college
AddPlayerResponse = dict[str, Any]  # message, player
TeamPlayersResponse = dict[str, list[PlayerDict]]  # team key -> players
CollegeListResponse = dict[str, list[str]]  # colleges key
ErrorResponse = dict[str, str]  # error key
