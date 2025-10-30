FROM python:3.12-slim

ENV UV_CACHE_DIR=/root/.cache/uv

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

CMD ["uv", "run", "polymarket-agents", "--help"]
