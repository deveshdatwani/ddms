import os
from celery import Celery
import logging

logger = logging.Logger(__name__)
logger.setLevel(logging.INFO)

HOST = os.getenv("REDIS_HOST", "localhost")

app = Celery("celery_app",
             broker=f"redis://{HOST}:6379/0",
             backend=f"redis://{HOST}:6379/0")