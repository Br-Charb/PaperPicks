FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /backend

RUN pip install --no-cache-dir uv
COPY pyproject.toml ./
COPY app/ ./app/

ARG DEV=false
RUN if [ "$DEV" = "true" ]; then uv pip install --system -e ".[dev]"; else uv pip install --system .; fi

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
