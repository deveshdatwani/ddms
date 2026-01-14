import os
from celery import Celery
from PIL import Image
from model.models.huggingface_cloth_segmentation.process import main as segment_apparel
import logging

logger = logging.Logger(__name__)
logger.setLevel(logging.INFO)


config = os.getenv("USER_APP_ENV", "prod")


if config == "prod": 
    HOST = "redis"
else: 
    HOST = "127.0.0.1"


app = Celery("flask",
             broker=f"redis://{HOST}:6379/0",
             backend=f"redis://{HOST}:6379/0")


@app.task(name="tasks.infer")
def segment_apparel_task(image_path):
    image = Image.open(image_path)
    image = segment_apparel(image)
    image.save(image_path)
    return True