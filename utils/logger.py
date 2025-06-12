import logging
import os

os.makedirs("logs", exist_ok=True)

logger = logging.getLogger('database')
logger.setLevel(logging.ERROR)

if not logger.handlers:
    file_handler = logging.FileHandler('logs/database_errors.log')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
