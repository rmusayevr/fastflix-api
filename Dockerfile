FROM python:3.11-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim as runtime

WORKDIR /app

RUN groupadd -r appuser && useradd -r -g appuser appuser

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

COPY --chown=appuser:appuser --from=builder /root/.local /home/appuser/.local

ENV PATH=/home/appuser/.local/bin:$PATH

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