import logging
import os
from logging.handlers import RotatingFileHandler

os.makedirs("logs", exist_ok=True)
logger = logging.getLogger("log-handler")
logger.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler(
    "logs/log-handler.log", maxBytes=5 * 1024 * 1024, backupCount=5
)
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
