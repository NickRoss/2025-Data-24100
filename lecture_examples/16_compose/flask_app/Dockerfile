FROM astral/uv:python3.13-bookworm

WORKDIR /app

RUN apt-get update
RUN apt-get install -y sqlite3

# Copy pyproject.toml for dependency management
COPY pyproject.toml /app/

ENV PYTHONUNBUFFERED=1

RUN uv venv
RUN uv sync

CMD ["uv", "run", "python", "flask_app.py"]
