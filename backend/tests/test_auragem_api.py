# AuraGem backend regression suite: catalog, auth, uploads, jobs (real AI), files, projects/images, isolation, billing.
import io
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
import requests
from PIL import Image

from conftest import API, BASE_URL, IMG


def _poll(client, job_id, timeout=420):
    end = time.time() + timeout
    seen = set()
    while time.time() < end:
        j = client.get(f"{API}/jobs/{job_id}").json()
        seen.add(j["status"])
        if j["status"] not in ("queued", "processing"):
            j["_seen"] = seen
            return j
        time.sleep(5)
    raise AssertionError(f"job {job_id} timed out; statuses {seen}")


def _png(w, h):
    b = io.BytesIO()
    Image.new("RGB", (w, h), (200, 180, 50)).save(b, "PNG")
    return b.getvalue()


# ---------- catalog & auth ----------
class TestCatalogAuth:
    def test_catalog_public(self):
        d = requests.get(f"{API}/catalog").json()
        assert d["ai_mode"] == "live" and d["payments_mode"] == "demo"
        assert [p["id"] for p in d["plans"]] == ["free", "starter", "growth", "business"]
        assert [p["credits"] for p in d["plans"]] == [3, 20, 75, 300]
        assert len(d["categories"]) >= 7 and len(d["styles"]) >= 10

    @pytest.mark.parametrize("path", ["/me", "/dashboard", "/projects", "/jobs", "/images", "/billing/summary"])
    def test_protected_401(self, path):
        assert requests.get(f"{API}{path}").status_code == 401
        assert requests.get(f"{API}{path}", headers={"Authorization": "Bearer garbage"}).status_code == 401

    @pytest.mark.parametrize("path", ["/me", "/dashboard", "/projects", "/jobs", "/images", "/billing/summary"])
    def test_protected_200(self, client_a, path):
        r = client_a.get(f"{API}{path}")
        assert r.status_code == 200, r.text

    def test_me_fields(self, client_a):
        d = client_a.get(f"{API}/me").json()
        assert d["email"].startswith("smoke") and isinstance(d["credits"], int) and "_id" not in d


# ---------- uploads ----------
class TestUploads:
    def test_upload_ok(self, upload_a):
        assert upload_a["width"] == 900 and upload_a["height"] == 600 and upload_a["url"].startswith("/api/files/upload/")
        assert requests.get(BASE_URL + upload_a["url"]).status_code == 200

    def test_upload_non_image(self, client_a):
        r = client_a.post(f"{API}/uploads", files={"file": ("x.jpg", b"not an image at all" * 50, "image/jpeg")})
        assert r.status_code == 422, r.text

    def test_upload_too_small(self, client_a):
        r = client_a.post(f"{API}/uploads", files={"file": ("s.png", _png(100, 100), "image/png")})
        assert r.status_code == 422, r.text

    def test_upload_too_large(self, client_a):
        r = client_a.post(f"{API}/uploads", files={"file": ("big.jpg", b"\xff\xd8" + b"0" * (16 * 1024 * 1024), "image/jpeg")})
        assert r.status_code == 413, (r.status_code, r.text[:200])


# ---------- jobs (real AI) ----------
class TestJobs:
    @pytest.fixture(scope="class")
    def jobs(self, client_a, upload_a):
        before = client_a.get(f"{API}/me").json()["credits"]
        specs = {
            "product": {"mode": "product", "upload_id": upload_a["id"], "category": "ring", "style": "luxury_black", "output_count": 1},
            "model": {"mode": "model", "upload_id": upload_a["id"], "category": "ring", "settings": {"preset": "modern_fashion"}, "output_count": 1},
            "bg": {"mode": "bg_removal", "upload_id": upload_a["id"], "category": "ring"},
        }
        created = {}
        for k, body in specs.items():
            r = client_a.post(f"{API}/jobs", json=body)
            assert r.status_code == 202, r.text
            created[k] = r.json()
        after = client_a.get(f"{API}/me").json()["credits"]
        with ThreadPoolExecutor(3) as ex:
            done = dict(zip(created, ex.map(lambda j: _poll(client_a, j["id"]), created.values())))
        return {"created": created, "done": done, "before": before, "after_reserve": after}

    def test_credits_reserved(self, jobs):
        assert jobs["before"] - jobs["after_reserve"] == 3
        assert jobs["created"]["product"]["status"] == "queued"
        assert jobs["created"]["product"]["credits_reserved"] == 1

    @pytest.mark.parametrize("k", ["product", "model", "bg"])
    def test_job_completed_with_quality(self, jobs, k):
        j = jobs["done"][k]
        assert j["status"] == "completed", (j["status"], j.get("error"), j.get("failures"))
        assert len(j["outputs"]) == 1
        q = j["outputs"][0]["quality"]
        for f in ("score", "verdict", "label", "issues"):
            assert f in q, q
        print(k, q)

    def test_bg_png(self, jobs):
        o = jobs["done"]["bg"]["outputs"][0]
        assert o["content_type"] == "image/png"
        r = requests.get(BASE_URL + o["url"])
        assert r.status_code == 200 and r.headers["content-type"] == "image/png"
        assert Image.open(io.BytesIO(r.content)).mode in ("RGBA", "LA", "P")

    def test_signed_urls(self, jobs):
        j = jobs["done"]["product"]
        url = j["outputs"][0]["url"]
        r = requests.get(BASE_URL + url)
        assert r.status_code == 200 and r.headers["content-type"].startswith("image/")
        bad = url[:-3] + ("aaa" if not url.endswith("aaa") else "bbb")
        assert requests.get(BASE_URL + bad).status_code == 403
        z = requests.get(BASE_URL + j["zip_url"])
        assert z.status_code == 200 and z.headers["content-type"] == "application/zip" and z.content[:2] == b"PK"
        d = requests.get(BASE_URL + j["outputs"][0]["download_url"])
        assert "attachment" in d.headers.get("content-disposition", "")

    def test_rerun(self, client_a, jobs):
        pid = jobs["done"]["product"]["id"]
        r = client_a.post(f"{API}/jobs/{pid}/rerun", json={"output_count": 1})
        assert r.status_code == 202, r.text
        nj = r.json()
        assert nj["parent_job_id"] == pid and nj["id"] != pid and nj["style"] == "luxury_black"
        done = _poll(client_a, nj["id"])
        assert done["status"] == "completed", done.get("error")

    def test_unknown_category_style(self, client_a, upload_a):
        r = client_a.post(f"{API}/jobs", json={"mode": "product", "upload_id": upload_a["id"], "category": "crown", "style": "marble"})
        assert r.status_code == 422
        r = client_a.post(f"{API}/jobs", json={"mode": "product", "upload_id": upload_a["id"], "category": "ring", "style": "space"})
        assert r.status_code == 422

    def test_list_jobs_mode_filter(self, client_a, jobs):
        lst = client_a.get(f"{API}/jobs?mode=bg_removal").json()
        assert lst and all(j["mode"] == "bg_removal" for j in lst)


# ---------- insufficient credits / isolation (user B) ----------
class TestIsolationCredits:
    def test_402_insufficient(self, client_b):
        me = client_b.get(f"{API}/me").json()
        with open(IMG, "rb") as f:
            up = client_b.post(f"{API}/uploads", files={"file": ("ring.jpg", f, "image/jpeg")}).json()
        if me["credits"] >= 4:
            pytest.skip(f"user B has {me['credits']} credits")
        r = client_b.post(f"{API}/jobs", json={"mode": "product", "upload_id": up["id"], "category": "ring", "style": "marble", "output_count": 4})
        assert r.status_code == 402, r.text
        assert client_b.get(f"{API}/me").json()["credits"] == me["credits"]

    def test_cross_user_404(self, client_a, client_b, upload_a):
        a_jobs = client_a.get(f"{API}/jobs?limit=1").json()
        p = client_a.post(f"{API}/projects", json={"name": "TEST_iso_proj"}).json()
        try:
            if a_jobs:
                assert client_b.get(f"{API}/jobs/{a_jobs[0]['id']}").status_code == 404
                assert client_b.post(f"{API}/jobs/{a_jobs[0]['id']}/rerun", json={}).status_code == 404
                if a_jobs[0]["outputs"]:
                    iid = a_jobs[0]["outputs"][0]["id"]
                    assert client_b.patch(f"{API}/images/{iid}", json={"project_id": None}).status_code == 404
                    assert client_b.delete(f"{API}/images/{iid}").status_code == 404
            assert client_b.get(f"{API}/projects/{p['id']}").status_code == 404
            assert client_b.delete(f"{API}/projects/{p['id']}").status_code == 404
            assert all(x["id"] != p["id"] for x in client_b.get(f"{API}/projects").json())
            r = client_b.post(f"{API}/jobs", json={"mode": "product", "upload_id": upload_a["id"], "category": "ring", "style": "marble"})
            assert r.status_code == 404
        finally:
            client_a.delete(f"{API}/projects/{p['id']}")


# ---------- projects & images ----------
class TestProjects:
    def test_project_crud_search_filter(self, client_a):
        r = client_a.post(f"{API}/projects", json={"name": "TEST_Bridal Rings", "description": "d", "category": "ring"})
        assert r.status_code == 201
        p = r.json()
        try:
            assert client_a.get(f"{API}/projects/{p['id']}").json()["name"] == "TEST_Bridal Rings"
            assert any(x["id"] == p["id"] for x in client_a.get(f"{API}/projects", params={"q": "bridal ri"}).json())
            assert not any(x["id"] == p["id"] for x in client_a.get(f"{API}/projects", params={"q": "zzznope"}).json())
            assert any(x["id"] == p["id"] for x in client_a.get(f"{API}/projects", params={"category": "ring"}).json())
            assert not any(x["id"] == p["id"] for x in client_a.get(f"{API}/projects", params={"category": "necklace"}).json())
            u = client_a.patch(f"{API}/projects/{p['id']}", json={"name": "TEST_Renamed", "category": "ring"})
            assert u.status_code == 200 and u.json()["name"] == "TEST_Renamed"
            assert client_a.post(f"{API}/projects", json={"name": "x", "category": "crown"}).status_code == 422
            assert client_a.post(f"{API}/projects", json={"name": ""}).status_code == 422
        finally:
            assert client_a.delete(f"{API}/projects/{p['id']}").status_code == 200
        assert client_a.get(f"{API}/projects/{p['id']}").status_code == 404

    def test_image_move_and_delete(self, client_a):
        imgs = client_a.get(f"{API}/images").json()["items"]
        if not imgs:
            pytest.skip("no images")
        img = imgs[-1]
        p = client_a.post(f"{API}/projects", json={"name": "TEST_move"}).json()
        try:
            r = client_a.patch(f"{API}/images/{img['id']}", json={"project_id": p["id"]})
            assert r.status_code == 200 and r.json()["project_id"] == p["id"]
            got = client_a.get(f"{API}/images", params={"project_id": p["id"]}).json()
            assert got["total"] == 1 and got["items"][0]["id"] == img["id"]
            assert client_a.get(f"{API}/projects/{p['id']}").json()["image_count"] == 1
            assert client_a.patch(f"{API}/images/{img['id']}", json={"project_id": "nope"}).status_code == 404
        finally:
            client_a.delete(f"{API}/projects/{p['id']}")
        # project delete (keep images) unassigns
        assert client_a.get(f"{API}/images").json()["items"][-1]["project_id"] is None

    def test_image_soft_delete(self, client_a):
        jobs = [j for j in client_a.get(f"{API}/jobs?mode=product").json() if j["outputs"] and j.get("parent_job_id")]
        if not jobs:
            pytest.skip("no rerun job image to delete")
        iid = jobs[0]["outputs"][0]["id"]
        url = jobs[0]["outputs"][0]["url"]
        assert client_a.delete(f"{API}/images/{iid}").status_code == 200
        assert all(i["id"] != iid for i in client_a.get(f"{API}/images?limit=200").json()["items"])
        assert client_a.delete(f"{API}/images/{iid}").status_code == 404
        assert requests.get(BASE_URL + url).status_code == 404


# ---------- billing (demo) ----------
class TestBilling:
    def test_order_demo_complete_idempotent_cancel(self, client_a):
        before = client_a.get(f"{API}/billing/summary").json()
        assert before["payments_mode"] == "demo"
        r = client_a.post(f"{API}/billing/orders", json={"plan_id": "starter"})
        assert r.status_code == 201, r.text
        o = r.json()
        assert o["mode"] == "demo" and o["amount"] == 129900 and o["key_id"] is None
        assert client_a.post(f"{API}/billing/demo-complete", json={"order_id": o["order_id"]}).status_code == 200
        mid = client_a.get(f"{API}/billing/summary").json()
        assert mid["credits"] == before["credits"] + 20
        assert mid["plan"] == "starter" and mid["subscription"]["status"] == "active" and mid["subscription"]["plan_id"] == "starter"
        assert any(t["kind"] if "kind" in t else True for t in mid["transactions"])
        assert client_a.post(f"{API}/billing/demo-complete", json={"order_id": o["order_id"]}).status_code == 200
        assert client_a.get(f"{API}/me").json()["credits"] == mid["credits"]
        c = client_a.post(f"{API}/billing/cancel").json()
        assert c["ok"] and c["cancelled"] >= 1
        assert client_a.get(f"{API}/billing/summary").json()["subscription"] is None

    def test_order_invalid_plan(self, client_a):
        assert client_a.post(f"{API}/billing/orders", json={"plan_id": "free"}).status_code == 404
        assert client_a.post(f"{API}/billing/orders", json={"plan_id": "zzz"}).status_code == 404

    def test_demo_complete_other_user(self, client_a, client_b):
        o = client_a.post(f"{API}/billing/orders", json={"plan_id": "growth"}).json()
        assert client_b.post(f"{API}/billing/demo-complete", json={"order_id": o["order_id"]}).status_code == 404

    def test_webhook_bad_sig(self):
        r = requests.post(f"{API}/billing/webhook", data=b'{"event":"payment.captured"}', headers={"X-Razorpay-Signature": "bad"})
        assert r.status_code == 400

    def test_verify_rejected_in_demo(self, client_a):
        o = client_a.post(f"{API}/billing/orders", json={"plan_id": "starter"}).json()
        r = client_a.post(f"{API}/billing/verify", json={"order_id": o["order_id"], "payment_id": "x", "signature": "y"})
        assert r.status_code == 400
