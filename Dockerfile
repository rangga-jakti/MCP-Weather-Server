# ── builder ──────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

RUN pip install --upgrade pip

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir ".[dev]" && \
    pip install --no-cache-dir -e .

# ── runtime ──────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY src/ src/

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from weather.server import mcp; print('ok')" || exit 1

CMD ["python", "-m", "weather.server"]
