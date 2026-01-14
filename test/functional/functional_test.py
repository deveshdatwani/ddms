import sys
import pytest 
import importlib
from PIL import Image
import io


def test_home(client):
    response = client.get('/app/')
    assert response.status_code == 200
    assert b"Closetx" in response.data


def test_user_registration(client):
    response = client.post('/app/register', data={"username":"deveshdatwani",
                                           "email":"deveshd@bolt6.ai",
                                           "password":"password"})
    assert response.status_code == 200
    assert b"User registered successfully" in response.data


def test_user_login(client):
    response = client.post('/app/login', data={"username":"deveshdatwani",
                                           "password":"password"})
    assert response.status_code == 200
    assert b"Login success"   in response.data and b"details" in response.data 


def test_add_apparel(client):
    image = Image.open('/home/deveshdatwani/closetx/ml_app/models/dataset/positive/top/cn55717004.jpg')
    bio = io.BytesIO()
    image.save(bio, format="JPEG")
    bio.seek(0)
    response = client.post('/app/closet', 
                       data={"userid": 1, 
                             "image": (bio, "image.jpg")},
                       content_type='multipart/form-data')
    assert response.status_code == 201
    # assert b"Login success"   in response.data and b"details" in response.data 


def test_user__z_deletion(client):
    client.delete('/app/delete/all', data={"userid":1})
    response = client.delete('/app/delete', data={"username":"deveshdatwani",
                                           "password":"password"})
    assert response.status_code == 200
    assert b"User deleted" in response.data