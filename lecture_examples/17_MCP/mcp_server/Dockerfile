FROM astral/uv:python3.13-bookworm

WORKDIR /app

# Copy pyproject.toml for dependency management
COPY pyproject.toml /app/

ENV PYTHONUNBUFFERED=1

# Create virtual environment and install dependencies
RUN uv venv
RUN uv sync
