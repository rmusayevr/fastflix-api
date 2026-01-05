import logging
import sys
import structlog
from app.core.config import settings


def setup_logging():
    """
    Configures structlog to output JSON in production
    and colored strings in development.
    """

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # 2. Environment Specific Formatting
    if settings.ENVIRONMENT == "prod":
        processors.extend(
            [
                structlog.processors.dict_tracebacks,
                structlog.processors.JSONRenderer(),
            ]
        )
    else:
        processors.extend(
            [
                structlog.dev.ConsoleRenderer(),
            ]
        )

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=logging.INFO)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
