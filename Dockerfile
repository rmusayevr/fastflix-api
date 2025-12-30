FROM python:3.11-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.11-slim as runtime

WORKDIR /app

RUN groupadd -r appuser && useradd -r -g appuser appuser

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY ./app ./app
COPY ./alembic ./alembic
COPY ./alembic.ini .
COPY ./prestart.sh .
COPY ./gunicorn_conf.py .

RUN chown -R appuser:appuser /app
RUN chmod +x /app/prestart.sh

USER appuser

ENTRYPOINT ["./prestart.sh"]
CMD ["gunicorn", "-c", "gunicorn_conf.py", "app.main:app"]