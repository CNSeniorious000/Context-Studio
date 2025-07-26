FROM python:3.13-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /app

COPY pyproject.toml .

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN uv sync --compile-bytecode --no-cache

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["python", "-Om", "uvicorn", "main:app", "--host", "0.0.0.0"]
