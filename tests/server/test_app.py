import pytest
import requests
import cv2

def test_preprocess_success():
    r = requests.get('http://localhost:8000/preprocess')
    assert str(r.content) == "b'done preprocessing data: success!'"
