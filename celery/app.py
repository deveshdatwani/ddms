import time 
import random
import logging
from celery_app import add_two_numbers

logger = logging.Logger(__name__)
logger.setLevel(logging.INFO)

while True:
    logger.info("Submitting a new addition task")
    print("Submitting a new addition task")
    print(add_two_numbers.delay(random.randint(1, 100), random.randint(1, 100)).get())
    time.sleep(5)