#!/bin/bash

echo "Running database migrations..."
alembic upgrade head

echo "Starting server..."
exec "$@"
```

**Make it executable and update Dockerfile again:**
```bash
chmod +x prestart.sh
```

**Final Dockerfile `CMD` update:**
```dockerfile
COPY ./prestart.sh .
ENTRYPOINT ["./prestart.sh"]
CMD ["gunicorn", "-c", "gunicorn_conf.py", "app.main:app"]