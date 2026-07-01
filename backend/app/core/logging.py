import logging


def configure_logging(level: str | None = None, service: str = "api") -> None:
    log_level = level or "INFO"
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s service=%(service)s request_id=%(request_id)s %(message)s",
    )


def get_logger(service: str = "api") -> logging.LoggerAdapter:
    logger = logging.getLogger(service)
    return logging.LoggerAdapter(logger, {"service": service, "request_id": "-"})
