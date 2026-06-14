import logging
import os

def setup_logging():
    os.makedirs("logs", exist_ok=True)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO)
    app_handler = logging.FileHandler("logs/log.log", mode="w", encoding="utf-8")
    app_handler.setFormatter(formatter)
    app_logger.addHandler(app_handler)

    error_logger = logging.getLogger("error")
    error_logger.setLevel(logging.ERROR)
    error_handler = logging.FileHandler("logs/errors.log", mode="w", encoding="utf-8")
    error_handler.setFormatter(formatter)
    error_logger.addHandler(error_handler)
