import os
import secrets
import pytest

os.environ.setdefault("FLASK_SECRET_KEY", "test-secret-key-for-testing")

from unittest.mock import patch, MagicMock
from lucid_web import app, _user_states, _get_state


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_csrf_token"] = "test-csrf-token"
        yield client


@pytest.fixture
def authenticated_client(client):
    """Client with a mocked API session."""
    with client.session_transaction() as sess:
        sid = secrets.token_hex(16)
        sess["sid"] = sid
    _user_states[sess["sid"]] = {
        "apikey": "fake-key",
        "api": MagicMock(),
        "selected_api": "chatgpt",
        "is_first_prompt": True,
    }
    _user_states[sess["sid"]]["api"].get_formatted_messages.return_value = []
    return client


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

class TestHealthRoute:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"


# ---------------------------------------------------------------------------
# Login page
# ---------------------------------------------------------------------------

class TestLogin:
    def test_login_get(self, client):
        resp = client.get("/login")
        assert resp.status_code == 200
        assert b"Login" in resp.data or b"login" in resp.data

    def test_login_redirects_when_no_api(self, client):
        resp = client.post("/login", data={
            "apikey": "",
            "apiplatform": "chatgpt",
            "_csrf_token": "test-csrf-token",
        })
        assert resp.status_code == 400

    def test_login_invalid_platform(self, client):
        resp = client.post("/login", data={
            "apikey": "fake-key",
            "apiplatform": "invalid_platform",
            "_csrf_token": "test-csrf-token",
        })
        assert resp.status_code == 400

    def test_login_csrf_missing(self, client):
        resp = client.post("/login", data={
            "apikey": "fake-key",
            "apiplatform": "chatgpt",
        })
        assert resp.status_code == 403

    def test_login_csrf_wrong(self, client):
        resp = client.post("/login", data={
            "apikey": "fake-key",
            "apiplatform": "chatgpt",
            "_csrf_token": "wrong-token",
        })
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Index route
# ---------------------------------------------------------------------------

class TestIndex:
    def test_index_requires_api(self, client):
        resp = client.get("/")
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

    def test_index_with_auth(self, authenticated_client):
        resp = authenticated_client.get("/")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# AJAX route
# ---------------------------------------------------------------------------

class TestAjax:
    def test_ajax_requires_api(self, client):
        resp = client.get("/ajax")
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

    def test_ajax_get_with_auth(self, authenticated_client):
        resp = authenticated_client.get("/ajax")
        assert resp.status_code == 200

    def test_ajax_post_csrf_required(self, authenticated_client):
        resp = authenticated_client.post("/ajax", data={
            "newMessage": "hello",
        })
        assert resp.status_code == 403

    def test_ajax_post_with_csrf(self, authenticated_client):
        resp = authenticated_client.post("/ajax", data={
            "newMessage": "hello",
            "_csrf_token": "test-csrf-token",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["successful"] == "true"

    def test_ajax_reset_api(self, authenticated_client):
        resp = authenticated_client.post("/ajax", data={
            "newMessage": "RESET_API",
            "_csrf_token": "test-csrf-token",
        })
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]


# ---------------------------------------------------------------------------
# Requirements route (/req)
# ---------------------------------------------------------------------------

class TestReq:
    def test_req_requires_api(self, client):
        resp = client.post("/req")
        assert resp.status_code == 302

    def test_req_with_auth_and_param(self, authenticated_client):
        resp = authenticated_client.post("/req", data={
            "request_messages": "true",
        })
        assert resp.status_code == 200

    def test_req_missing_param(self, authenticated_client):
        resp = authenticated_client.post("/req", data={})
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Test route
# ---------------------------------------------------------------------------

class TestTestRoute:
    def test_test_route(self, client):
        resp = client.get("/test")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# No breakpoint in code
# ---------------------------------------------------------------------------

class TestNoBreakpoints:
    def test_no_breakpoint_in_source(self):
        with open("lucid_web.py", "r") as f:
            content = f.read()
        assert "breakpoint()" not in content, "breakpoint() found in lucid_web.py!"

    def test_no_breakpoint_in_source_files(self):
        """Check that no source file has breakpoint() in production code."""
        import glob
        for py_file in glob.glob("**/*.py", recursive=True):
            if ".venv" in py_file or "tests/" in py_file:
                continue
            with open(py_file, "r", errors="ignore") as f:
                content = f.read()
            # Allow breakpoint in test files and checkpoint/bmain (unused)
            if "tests/" in py_file or "checkpoint.py" in py_file or "bmain.py" in py_file:
                continue
            assert "breakpoint()" not in content, f"breakpoint() found in {py_file}!"
