"""
Business Logic Tests for User Service Authentication

These tests check for security and authentication logic bugs.
To enable a test, remove the @pytest.mark.skip decorator.
To trigger a failure, uncomment the corresponding bug in services/user-service/app.py
"""
import pytest
import importlib.util
import pathlib
from prometheus_client import REGISTRY


def load_app():
    """Load user-service app"""
    # Clear registry to avoid duplicate metrics error on reload
    for collector in list(REGISTRY._collector_to_names.keys()):
        try:
            REGISTRY.unregister(collector)
        except KeyError:
            pass

    p = pathlib.Path("services/user-service/app.py")
    spec = importlib.util.spec_from_file_location("user_app", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.app


@pytest.mark.skip(reason="Enable this test to check authentication logic")
def test_wrong_password_rejected():
    """
    BUG SCENARIO 1: Authentication Bypass

    Test that wrong password is rejected.

    TO TRIGGER THIS TEST FAILURE:
    In services/user-service/app.py, line 74, change:
        if not user or user["password_hash"] != hash_pw(password):
    To:
        if not user:  # BUG: Removed password check!

    Then remove @pytest.mark.skip from this test.
    """
    app = load_app()
    client = app.test_client()

    # Register user with correct password
    client.post("/register", json={
        "username": "alice",
        "password": "correct_password",
        "name": "Alice",
        "email": "alice@example.com"
    })

    # Try to login with WRONG password - should fail
    response = client.post("/login", json={
        "username": "alice",
        "password": "WRONG_PASSWORD"
    })

    # This assertion will FAIL if authentication bug exists
    assert response.status_code == 401, "Wrong password should be rejected!"
    assert "error" in response.get_json(), "Should return error message"
    assert "invalid credentials" in response.get_json()["error"].lower()


@pytest.mark.skip(reason="Enable this test to check empty username handling")
def test_empty_username_rejected():
    """
    BUG SCENARIO 2: Input Validation Failure

    Test that empty username is rejected during registration.

    TO TRIGGER THIS TEST FAILURE:
    In services/user-service/app.py, line 50, change:
        if not username or not password:
    To:
        if not password:  # BUG: Only checking password!

    Then remove @pytest.mark.skip from this test.
    """
    app = load_app()
    client = app.test_client()

    # Try to register with empty username
    response = client.post("/register", json={
        "username": "",
        "password": "somepassword",
        "name": "Test User",
        "email": "test@example.com"
    })

    # Should be rejected
    assert response.status_code == 400, "Empty username should be rejected!"
    assert "error" in response.get_json()


@pytest.mark.skip(reason="Enable this test to check token validation")
def test_invalid_token_rejected():
    """
    BUG SCENARIO 3: Token Validation Bypass

    Test that invalid/tampered tokens are rejected.

    TO TRIGGER THIS TEST FAILURE:
    In services/user-service/app.py, line 86, change:
        if not username or username not in USERS:
    To:
        if not username:  # BUG: Doesn't check if user exists!

    Then remove @pytest.mark.skip from this test.
    """
    app = load_app()
    client = app.test_client()

    # Try to access profile with fake token
    response = client.get("/profile", headers={
        "Authorization": "Bearer fake_invalid_token_12345"
    })

    # Should be rejected
    assert response.status_code == 401, "Invalid token should be rejected!"
    assert "error" in response.get_json()
