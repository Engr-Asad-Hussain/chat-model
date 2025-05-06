FROM python:3.10-slim

ENV UV_COMPILE_BYTE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY uv.lock pyproject.toml ./
RUN uv sync --frozen --no-install-project --no-dev

COPY app ./app
COPY manage.py ./

CMD ["uv", "run", "manage.py"]
