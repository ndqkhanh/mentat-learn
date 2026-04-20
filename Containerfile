# Self-contained Dockerfile — builds from this project folder only.
# docker build -t mentat-learn -f Dockerfile .
FROM python:3.11-slim

WORKDIR /app


COPY pyproject.toml ./pyproject.toml
COPY src ./src
COPY tests ./tests
RUN pip install --no-cache-dir -e '.[dev]'

ENV PYTHONUNBUFFERED=1
EXPOSE 8008

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8008/healthz', timeout=2)" || exit 1

CMD ["uvicorn", "mentat_learn.app:app", "--host", "0.0.0.0", "--port", "8008"]
