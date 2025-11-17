"""Database query utilities for managing basketball player and college data.

This module provides functions for querying and modifying player statistics
and college information in the SQLite database.
"""

from sqlite3 import Connection
from typing import Any

from app.data_utils.loading_utils import (
    create_db_connection,
    execute_query_return_list_of_dicts_lm,
)


def list_college_sql(team: str | None = None) -> list[str]:
    """Get list of colleges for all players or players from a specific team.

    Args:
        team: Team abbreviation to filter by

    Returns:
        List of college names
    """
    conn: Connection = create_db_connection()

    if team is None:
        list_colleges_query = (
            "SELECT distinct college from player_stats "
            " where season = '2022-23';"
        )
    else:
        list_colleges_query = (
            "SELECT distinct college from player_stats "
            f" where team_abbreviation = '{team}' and "
            " season = '2022-23';"
        )

    sql_results_dict = execute_query_return_list_of_dicts_lm(
        conn, list_colleges_query
    )

    return [x["college"] for x in sql_results_dict]


def list_players_per_team_sql(
    team: str | None = None,
) -> list[dict[str, str | int]]:
    """Get list of players and their IDs for all teams or a specific team.

    Args:
        team: Team abbreviation to filter by

    Returns:
        List of dicts containing player names and IDs
    """
    conn: Connection = create_db_connection()

    if team is None:
        list_query = (
            "SELECT distinct player_name, id from player_stats "
            " where season = '2022-23';"
        )
    else:
        list_query = (
            "SELECT distinct player_name, id from player_stats "
            f" where team_abbreviation = '{team}' and "
            " season = '2022-23';"
        )

    return execute_query_return_list_of_dicts_lm(conn, list_query)


def add_player(player_info: dict[str, Any]) -> None:
    """Add a new player to the database.

    Args:
        player_info: Dict containing player information including:
            - player_name (str): Player's full name
            - team (str): Team abbreviation
            - college (Optional[str]): Player's college
    """
    conn: Connection = create_db_connection()
    query = """
    INSERT INTO player_stats
    (player_name, team_abbreviation, college, season)
    VALUES
    (?, ?, ?, '2022-23')
    """

    params = (
        player_info["player_name"],
        player_info["team"],
        player_info.get("college"),
    )

    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()


def delete_player(player_id: int) -> str:
    """Delete a player by ID and return their name.

    Args:
        player_id: ID of player to delete

    Returns:
        Name of deleted player

    Raises:
        ValueError: If no player found with given ID
    """
    conn: Connection = create_db_connection()

    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT player_name
        FROM player_stats
        WHERE id = ?
        AND season = '2022-23'
        LIMIT 1
        """,
        (player_id,),
    )
    result = cursor.fetchone()

    if not result:
        raise ValueError(f"No player found with ID: {player_id}")

    player_name: str = result[0]

    cursor.execute(
        """
        DELETE FROM player_stats
        WHERE id = ?
        AND season = '2022-23'
        """,
        (player_id,),
    )
    conn.commit()

    return player_name


def all_teams_sql() -> list[str]:
    """Get list of all teams.

    Returns:
        List of unique team abbreviations
    """
    conn: Connection = create_db_connection()
    team_query = (
        "select distinct team_abbreviation from player_stats "
        " where season = '2022-23'"
    )

    sql_results_dict = execute_query_return_list_of_dicts_lm(conn, team_query)
    return [x["team_abbreviation"] for x in sql_results_dict]


def player_info_sql(player_id: int) -> list[dict[str, Any]]:
    """Get detailed information for a specific player.

    Args:
        player_id: Player's ID in database

    Returns:
        List containing dict with player information
    """
    conn: Connection = create_db_connection()

    player_query = (
        f"select * from player_stats where id = {player_id} "
        " and season = '2022-23'"
    )

    return execute_query_return_list_of_dicts_lm(conn, player_query)
