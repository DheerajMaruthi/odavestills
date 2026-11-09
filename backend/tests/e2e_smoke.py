"""Manual smoke test against a running backend: python tests/e2e_smoke.py <api_base> <image_path>"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
SK = os.environ["CLERK_SECRET_KEY"]


def bapi(path, body=None, method="POST"):
    req = urllib.request.Request("https://api.clerk.com/v1" + path, data=json.dumps(body).encode() if body is not None else None, method=method,
                                 headers={"Authorization": "Bearer " + SK, "Content-Type": "application/json", "User-Agent": "auragem-test"})
    return json.load(urllib.request.urlopen(req))


def token_for(email):
    users = bapi(f"/users?email_address={urllib.parse.quote(email)}", method="GET")
    user = users[0] if users else bapi("/users", {"email_address": [email], "password": "Test-pass-12345!", "skip_password_checks": True})
    sess = bapi("/sessions", {"user_id": user["id"]})
    return bapi(f"/sessions/{sess['id']}/tokens", {"expires_in_seconds": 3600})["jwt"], user["id"]


if __name__ == "__main__":
    base, img = sys.argv[1], sys.argv[2]
    tok, uid = token_for("smoke+clerk_test@example.com")
    h = {"Authorization": f"Bearer {tok}"}
    print("me", requests.get(f"{base}/me", headers=h).json()["credits"])
    up = requests.post(f"{base}/uploads", headers=h, files={"file": ("ring.jpg", open(img, "rb"), "image/jpeg")}).json()
    print("upload", up.get("width"), up.get("height"))
    for mode, style in (("product", "marble"), ("bg_removal", None)):
        job = requests.post(f"{base}/jobs", headers=h, json={"mode": mode, "upload_id": up["id"], "category": "ring", "style": style}).json()
        print("job", mode, job.get("id"), job.get("status"), job.get("detail"))
        while job.get("status") in ("queued", "processing"):
            time.sleep(5)
            job = requests.get(f"{base}/jobs/{job['id']}", headers=h).json()
        print(mode, job["status"], job.get("error"), [o["quality"].get("score") for o in job["outputs"]], [o["quality"].get("issues") for o in job["outputs"]])
