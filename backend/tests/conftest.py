import json
import os
import urllib.parse
import urllib.request

import pytest
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", ".env"))
BASE_URL = os.environ.get("REACT_APP_BACKEND_URL").rstrip("/")
API = f"{BASE_URL}/api"
IMG = "/app/frontend/public/showcase/ring-before.jpg"
USER_A = "smoke+clerk_test@example.com"
USER_B = "test_isolation_b+clerk_test@example.com"


def _bapi(path, body=None, method="POST"):
    sk = os.environ["CLERK_SECRET_KEY"]
    req = urllib.request.Request("https://api.clerk.com/v1" + path, data=json.dumps(body).encode() if body is not None else None,
                                 method=method, headers={"Authorization": "Bearer " + sk, "Content-Type": "application/json",
                                                         "User-Agent": "auragem-test"})
    return json.load(urllib.request.urlopen(req))


def clerk_user(email):
    users = _bapi(f"/users?email_address={urllib.parse.quote(email)}", method="GET")
    return users[0] if users else _bapi("/users", {"email_address": [email], "password": "Test-pass-12345!", "skip_password_checks": True})


def token_for(email):
    user = clerk_user(email)
    sess = _bapi("/sessions", {"user_id": user["id"]})
    return _bapi(f"/sessions/{sess['id']}/tokens", {"expires_in_seconds": 3600})["jwt"], user["id"]


def sign_in_ticket(email):
    return _bapi("/sign_in_tokens", {"user_id": clerk_user(email)["id"]})["token"]


def _client(email):
    tok, uid = token_for(email)
    s = requests.Session()
    s.headers.update({"Authorization": f"Bearer {tok}"})
    s.user_id = uid
    return s


@pytest.fixture(scope="module")
def client_a():
    return _client(USER_A)


@pytest.fixture(scope="module")
def client_b():
    return _client(USER_B)


@pytest.fixture(scope="module")
def upload_a(client_a):
    with open(IMG, "rb") as f:
        r = client_a.post(f"{API}/uploads", files={"file": ("ring.jpg", f, "image/jpeg")})
    assert r.status_code == 201, r.text
    return r.json()
