import uuid
import boto3
import io, os
import requests
from PIL import Image, ExifTags
import mysql.connector
from base64 import encodebytes
from mysql.connector import errorcode
from flask import g, current_app, Response
from werkzeug.security import check_password_hash, generate_password_hash
from mysql import connector
from io import BytesIO
import base64
from celery import Celery


config = os.getenv("USER_APP_ENV", "prod")

if config == "prod":
    HOST = "redis"
else:
    HOST = "127.0.0.1"

celery_app = Celery("flask",
                    broker=f"redis://{HOST}:6379/0",
                    backend=f"redis://{HOST}:6379/0")


def serve_response(data: str, status_code: int):
    return Response(response=data, status=status_code)


def get_s3_boto_client():
    try:
        boto3.setup_default_session(
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
            region_name='us-east-2'
        )
        s3 = boto3.client('s3')
        current_app.logger.info("S3 client connected")
        return s3
    except Exception as e:
        current_app.logger.error(f"Failed to connect to S3: {e}")
        return None


def get_db_x():
    try:
        conn = mysql.connector.connect(
            database=current_app.config["DB_DATABASE"],
            user='closetx',
            password=current_app.config["DB_PASSWORD"],
            host=current_app.config["DB_HOST"],
            port=current_app.config["DB_PORT"],
        )
        current_app.logger.info("Successfully connected to MySQL")
        return conn
    except Exception as e:
        current_app.logger.error(f"MySQL connection error: {e}")
        return None


def register_user(username: str, password: str) -> bool:
    dbx = get_db_x()
    if not dbx: return False
    try:
        crx = dbx.cursor()
        auth_string = generate_password_hash(password)
        crx.execute("INSERT INTO user (username, password) VALUES (%s, %s)", (username, auth_string))
        dbx.commit()
        return True
    except Exception as e:
        current_app.logger.error(f"Error registering user: {e}")
        return False
    finally:
        crx.close()
        dbx.close()


def login_user(username, password):
    dbx = get_db_x()
    if not dbx:
        return None
    try:
        crx = dbx.cursor()
        crx.execute("SELECT * FROM user WHERE username = %s", (username,))
        user = crx.fetchone()
        if user and check_password_hash(user[2], password):
            current_app.logger.info("Password matches")
            return user
        else:
            current_app.logger.info("Incorrect password or user not found")
            return None
    except Exception as e:
        current_app.logger.error(f"Login error: {e}")
        return None
    finally:
        crx.close()
        dbx.close()


def get_user(username):
    dbx = get_db_x()
    if not dbx:
        return None
    try:
        crx = dbx.cursor()
        crx.execute("SELECT * FROM user WHERE username = %s", (username,))
        return crx.fetchone()
    except Exception as e:
        current_app.logger.error(f"Error fetching user: {e}")
        return None
    finally:
        crx.close()
        dbx.close()


def delete_user(username):
    dbx = get_db_x()
    if not dbx:
        return False
    try:
        crx = dbx.cursor()
        crx.execute("DELETE FROM user WHERE username = %s", (username,))
        dbx.commit()
        return True
    except Exception as e:
        current_app.logger.error(f"Error deleting user: {e}")
        return False
    finally:
        crx.close()
        dbx.close()


def post_apparel(userid, image):
    try:
        apparel_uuid = str(uuid.uuid4()) + ".png"
        max_size = (800, 800)
        image.thumbnail(max_size)
        image.save(f"/closet/.cache/{apparel_uuid}")
        celery_app.send_task("tasks.infer", args=[f"/closet/.cache/{apparel_uuid}"])
        dbx = get_db_x()
        s3_client = get_s3_boto_client()
        if not dbx or not s3_client:
            return False
        s3_client.upload_file(f"/closet/.cache/{apparel_uuid}", "closetx-images", apparel_uuid)
        crx = dbx.cursor()
        crx.execute("INSERT INTO apparel (user, uri) VALUES (%s, %s)", (userid, apparel_uuid))
        dbx.commit()
        current_app.logger.info("Inserted image into S3 and DB")
        return True
    except Exception as e:
        current_app.logger.error(f"Error in post_apparel: {e}")
        return False
    finally:
        try:
            crx.close()
            dbx.close()
        except:
            pass


def get_apparel(uri):
    try:
        cache_path = f"/closet/.cache/{uri}"
        if os.path.isfile(cache_path):
            current_app.logger.info("Located apparel in cache")
        else:
            s3 = get_s3_boto_client()
            if not s3:
                return None
            with open(cache_path, 'wb') as data:
                s3.download_fileobj('closetx-images', uri, data)
        apparel_image = Image.open(cache_path)
        img_io = io.BytesIO()
        apparel_image.save(img_io, 'PNG')
        img_io.seek(0)
        current_app.logger.info("Fetched image")
        return img_io
    except Exception as e:
        current_app.logger.error(f"Error in get_apparel: {e}")
        return None


def get_user_apparels(userid):
    dbx = get_db_x()
    if not dbx:
        return []
    try:
        crx = dbx.cursor()
        crx.execute("SELECT uri FROM apparel WHERE user = %s", (userid,))
        return crx.fetchall()
    except Exception as e:
        current_app.logger.error(f"Error fetching user apparels: {e}")
        return []
    finally:
        crx.close()
        dbx.close()


def delete_apparel(uri):
    dbx = get_db_x()
    if not dbx:
        return False
    try:
        crx = dbx.cursor()
        crx.execute("DELETE FROM apparel WHERE uri = %s", (uri,))
        dbx.commit()
        return True
    except Exception as e:
        current_app.logger.error(f"Error deleting apparel: {e}")
        return False
    finally:
        crx.close()
        dbx.close()


def delete_closet(userid):
    dbx = get_db_x()
    if not dbx:
        return False
    try:
        crx = dbx.cursor()
        crx.execute("DELETE FROM apparel WHERE user = %s", (userid,))
        dbx.commit()
        return True
    except Exception as e:
        current_app.logger.error(f"Error deleting closet: {e}")
        return False
    finally:
        crx.close()
        dbx.close()


def fetch_image_base64(s3_uri):
    try:
        img_io = get_apparel(s3_uri)
        if not img_io:
            return None
        encoded = base64.b64encode(img_io.read()).decode("utf-8")
        return encoded
    except Exception as e:
        current_app.logger.error(f"Error in fetch_image_base64: {e}")
        return None


def correct_image_orientation(image):
    try:
        image = Image.open(image.stream)
        exif = image._getexif()
        if exif is not None:
            orientation = next((k for k, v in ExifTags.TAGS.items() if v == 'Orientation'), None)
            orientation_value = exif.get(orientation)
            if orientation_value == 3:
                image = image.rotate(180, expand=True)
            elif orientation_value == 6:
                image = image.rotate(270, expand=True)
            elif orientation_value == 8:
                image = image.rotate(90, expand=True)
    except Exception as e:
        current_app.logger.error(f"EXIF orientation correction failed: {e}")
    return image
