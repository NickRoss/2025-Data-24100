"""Tests for the Flask application."""
import sys
from pathlib import Path

import pytest
from jsonschema import validate

# Add the src directory to the Python path so we can import the app
sys.path.append(str(Path(__file__).parent.parent.resolve()))

from flask_app import create_app  # noqa E402


@pytest.fixture
def app():
    """Create and configure a test instance of the application."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        # Add any test-specific configuration here
    })
    return app


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


def test_app_exists(app):
    """Test that the app exists."""
    assert app is not None


def test_app_is_testing(app):
    """Test that the app is in testing mode."""
    assert app.config["TESTING"]


def test_player_response(client):
    """Test the /api/players endpoint."""
    HTTP_OK = 200

    schema = {
        "type": "object",
        "properties": {
            "players": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "number"},
                        "player_name": {"type": "string"}
                    },
                    "required": ["id", "player_name"]
                }
            }
        },
        "required": ["players"]
    }
    response = client.get("/api/players")
    # Assert response is JSON
    assert response.status_code == HTTP_OK
    assert response.content_type == "application/json"

    # Assert we can parse the response as JSON
    json_data = response.get_json()
    validate(instance=json_data, schema=schema)

# Tests below should be used in the 2nd part of the lecture.
# They work

def test_list_players_per_team_response(client, team_to_test="WAS"):
    schema = {
        "type": "object",
        "properties": {
            team_to_test: {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "number"},
                        "player_name": {"type": "string"}
                    },
                    "required": ["id", "player_name"]
                }
            }
        },
        "required": [team_to_test]
    }
    response = client.get(f'/api/teams/players/{team_to_test}/list')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    validate(instance=response.get_json(), schema=schema)


def test_colleges_schema_response(client):
    """Test the /api/colleges/{team}/list endpoint schema."""
    HTTP_OK = 200

    schema = {
        "type": "object",
        "properties": {
            "colleges": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        },
        "required": ["colleges"]
    }

    response = client.get("/api/colleges/WAS/list")
    # Assert response is JSON
    assert response.status_code == HTTP_OK
    assert response.content_type == "application/json"

    # Assert we can parse the response as JSON
    json_data = response.get_json()
    validate(instance=json_data, schema=schema)


def test_WAS_colleges_exact_response(client):
    expected_response = {
        "colleges": [
            "Texas A&M",
            "Iowa State",
            "Winthrop",
            "Southern California",
            "Kansas",
            "None",
            "Utah",
            "Arkansas",
            "Virginia",
            "Florida",
            "Gonzaga",
            "Oakland",
            "San Francisco",
            "St. Louis",
            "San Diego State",
            "Wisconsin"
        ]
    }

    response = client.get('/api/colleges/WAS/list')
    assert response.status_code == 200
    assert response.content_type == 'application/json'

    # Get the actual response data
    actual_response = response.get_json()

    # Verify the structure
    assert "colleges" in actual_response
    assert isinstance(actual_response["colleges"], list)

    # Sort both lists and compare
    assert sorted(actual_response["colleges"]) \
        == sorted(expected_response["colleges"])
