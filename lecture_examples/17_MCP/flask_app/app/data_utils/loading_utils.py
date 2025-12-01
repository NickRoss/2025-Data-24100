"""Database and data loading utilities for basketball player statistics.

This module provides functions for creating, managing and querying SQLite,
as well as loading and transforming player statistics data.
"""

import csv
import os
import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = os.environ["DB_PATH"]
DATA_DIR = os.environ["DATA_DIR"]


def load_data_pandas() -> pd.DataFrame:
    """Load current season's player data into a DataFrame.

    Returns:
        pd.DataFrame: Player statistics filtered for current season
        with selected columns.
    """
    file_path = "/app/src/data/all_seasons.csv"
    players_df = pd.read_csv(file_path)
    players_df = players_df.loc[
        players_df.season == "2022-23",
        [
            "player_name",
            "college",
            "team_abbreviation",
        ],
    ]
    return players_df


def load_data() -> pd.DataFrame:
    """Load current season's player data using SQL.

    Returns:
        pd.DataFrame: Player statistics including ID, name, college and team.
    """
    conn = create_db_connection()
    query = """select id, player_name,
            college,
            team_abbreviation
        from player_stats
    where season = '2022-23';"""

    players_df = pd.DataFrame(
        execute_query_return_list_of_dicts_lm(conn, query)
    )
    return players_df


def create_db_connection(db_path: str | None = None) -> sqlite3.Connection:
    """Create a connection to the SQLite database.

    Args:
        db_path: Path to database file. Defaults to DB_PATH.

    Returns:
        sqlite3.Connection: Database connection object.

    Raises:
        FileExistsError: If database file doesn't exist.
    """
    if not db_path:
        db_path = DB_PATH

    db_file = Path(db_path)
    if not db_file.exists():
        raise FileExistsError(f"Database does not exist at: {db_path}")

    conn = sqlite3.connect(db_file)
    return conn


def execute_query_return_list_of_dicts_lm(
    conn: sqlite3.Connection, sql_query: str
) -> list[dict[str, str | int | float | None]]:
    """Execute SQL query and return results as list of dicts (low mem version).

    Args:
        conn: SQLite connection
        sql_query: SQL query to execute

    Returns:
        List[Dict]: Query results as list of dictionaries
    """
    cursor = conn.cursor()
    cursor.execute(sql_query)
    description_info = cursor.description

    headers = [x[0] for x in description_info]
    return_dict_list = []

    while True:
        single_result = cursor.fetchone()
        if not single_result:
            break

        single_result_dict = dict(zip(headers, single_result))
        return_dict_list.append(single_result_dict)

    return return_dict_list


def load_csv_to_db(
    conn: sqlite3.Connection, csv_path: str | Path, table_name: str
) -> bool:
    """Load a CSV file into an existing SQLite table.

    Args:
        conn: SQLite connection
        csv_path: Path to the CSV file
        table_name: Name of the existing table

    Returns:
        bool: True if loading was successful
    """
    csv_file = Path(csv_path)
    with csv_file.open() as f:
        reader = csv.reader(f)
        headers = next(reader)[1:]  # Get column names
        headers = ["id"] + headers

        placeholders = ",".join("?" for _ in headers)
        insert_sql = (
            f"INSERT INTO {table_name} ({','.join(headers)})"
            f" VALUES ({placeholders})"
        )
        cur = conn.cursor()
        cur.executemany(insert_sql, reader)
        conn.commit()
    print(f"Loaded {cur.rowcount} rows to {table_name} successfully")
    return True


def execute_sql_command(conn: sqlite3.Connection, sql_query: str) -> None:
    """Execute a SQL command and commit changes.

    Args:
        conn: SQLite connection
        sql_query: SQL command to execute
    """
    cur = conn.cursor()
    cur.execute(sql_query)
    conn.commit()


def create_player_stats_table(conn: sqlite3.Connection) -> None:
    """Create a table for basketball player statistics.

    Args:
        conn: SQLite connection
    """
    create_table_ball = """
    CREATE TABLE player_stats (
        id INTEGER PRIMARY KEY,
        player_name TEXT NOT NULL,
        team_abbreviation TEXT,
        age REAL,
        player_height REAL,
        player_weight REAL,
        college TEXT,
        country TEXT,
        draft_year INTEGER,
        draft_round INTEGER,
        draft_number INTEGER,
        gp INTEGER,            -- games played
        pts REAL,              -- points
        reb REAL,              -- rebounds
        ast REAL,              -- assists
        net_rating REAL,
        oreb_pct REAL,         -- offensive rebound percentage
        dreb_pct REAL,         -- defensive rebound percentage
        usg_pct REAL,          -- usage percentage
        ts_pct REAL,           -- true shooting percentage
        ast_pct REAL,          -- assist percentage
        season TEXT            -- storing as TEXT since it's in YYYY-YY format
    )
    """
    execute_sql_command(conn, create_table_ball)


def create_empty_sqlite_db(db_path: str | None = None) -> bool:
    """Create an empty SQLite database at the specified path.

    Args:
        db_path: Database file path. Defaults to DB_PATH.

    Returns:
        bool: True if database was created successfully

    Raises:
        FileExistsError: If database already exists at path.
    """
    if not db_path:
        db_path = DB_PATH

    db_file = Path(db_path)
    if db_file.exists():
        raise FileExistsError(f"Database already exists at {db_path}")

    db_file.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_file)
    conn.close()

    print(f"Database created at {db_path}")
    return True


def rm_db(db_path: str | None = None) -> None:
    """Delete the database file.

    Warning: This operation is not recoverable.

    Args:
        db_path: Path to database. Defaults to DB_PATH.
    """
    if not db_path:
        db_path = DB_PATH

    db_file = Path(db_path)
    if db_file.exists():
        db_file.unlink()

    print(f"Database at {db_path} removed")


def create_and_load_basketball_data(
    csv_path: str | Path, table_name: str
) -> None:
    """Create database tables and load basketball data from CSV.

    Args:
        csv_path: Path to CSV file containing basketball data
        table_name: Name of table to create and load data into
    """
    conn = create_db_connection()
    create_player_stats_table(conn)
    load_csv_to_db(conn, csv_path, table_name)
