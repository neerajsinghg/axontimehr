import logging
import sys
from typing import Any, Dict
from app.core.config import settings

try:
    from pythonjsonlogger import jsonlogger

    class ContextJsonFormatter(jsonlogger.JsonFormatter):
        def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
            super().add_fields(log_record, record, message_dict)
            log_record["app_name"] = settings.APP_NAME
            log_record["environment"] = settings.APP_ENV
            if not log_record.get("level"):
                log_record["level"] = record.levelname
            if not log_record.get("logger"):
                log_record["logger"] = record.name

    formatter_class = ContextJsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s %(request_id)s %(tenant_id)s %(user_id)s"
    )
except ImportError:
    formatter_class = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
    )

def setup_logging() -> logging.Logger:
    logger = logging.getLogger("axontime")
    log_level = logging.DEBUG if settings.APP_DEBUG else logging.INFO
    logger.setLevel(log_level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter_class)
        logger.addHandler(handler)

    return logger

logger = setup_logging()

