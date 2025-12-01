"""Flask application setup and initialization.

This module configures and creates the Flask application instance,
sets up logging, and registers API route blueprints.
"""

import logging

from flask_cors import CORS
from flask_openapi3 import Info, OpenAPI, Server

from app.api.colleges.routes import (
    register_college_routes,
)
from app.api.players.routes import (
    register_player_routes,
)
from app.api.teams.routes import (
    register_team_routes,
)
from app.logger_utils.custom_logger import custom_logger


def create_app():
    """Create and configure the Flask application instance.

    Returns:
        OpenAPI: Configured OpenAPI Flask application
    """
    info = Info(title="Basketball API", version="1.0.0")
    servers = [
        Server(url="http://localhost:4000", description="Local server"),
    ]
    app = OpenAPI(
        __name__,
        info=info,
        servers=servers,
        doc_ui=True,
        doc_prefix="/docs",
    )

    # Enable CORS for all routes with permissive settings for Swagger UI
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        expose_headers=["Content-Type", "Authorization"],
        allow_headers=["Content-Type", "Authorization"],
    )

    # Debug Level:
    debug_level = logging.DEBUG
    # Initialize logger
    app.logger = custom_logger  # Attach logger to Flask app
    app.logger.setLevel(debug_level)
    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.setLevel(debug_level)
    werkzeug_logger.handlers = []
    werkzeug_logger.addHandler(app.logger.handlers[0])

    register_player_routes(app)
    register_team_routes(app)
    register_college_routes(app)

    # Add alias for OpenAPI spec at /openapi/openapi.json for Swagger UI
    @app.route("/openapi/openapi.json")
    def openapi_spec_alias():
        """Redirect to the actual OpenAPI spec location."""
        from flask import redirect

        return redirect("/docs/openapi.json", code=301)

    app.logger.info("Application initialized successfully")
    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
