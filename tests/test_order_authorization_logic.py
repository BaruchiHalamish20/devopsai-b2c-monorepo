"""
Business Logic Tests for Order Service Authorization

These tests check for authorization and data isolation bugs.
To enable a test, remove the @pytest.mark.skip decorator.
To trigger a failure, uncomment the corresponding bug in services/order-service/app.py
"""
import pytest
import importlib.util
import pathlib


def load_app():
    """Load order-service app"""
    p = pathlib.Path("services/order-service/app.py")
    spec = importlib.util.spec_from_file_location("order_app", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.app


def get_test_token(username):
    """Generate a test authentication token for specific user"""
    from itsdangerous import URLSafeSerializer
    signer = URLSafeSerializer("dev-secret", salt="user-auth")
    return signer.dumps({"u": username})


@pytest.mark.skip(reason="Enable this test to check user order isolation")
def test_user_order_isolation():
    """
    BUG SCENARIO 1: Authorization Bypass - Data Leak

    Test that users can only see their own orders, not other users' orders.

    TO TRIGGER THIS TEST FAILURE:
    In services/order-service/app.py, line 122, change:
        user_orders = [o for o in ORDERS if o["user"] == username]
    To:
        user_orders = ORDERS  # BUG: Exposes all users' orders!

    Then remove @pytest.mark.skip from this test.
    """
    app = load_app()
    client = app.test_client()

    # Create tokens for two different users
    token_alice = get_test_token("alice")
    token_bob = get_test_token("bob")

    # Alice creates an order
    alice_order = client.post("/create_order",
        headers={"Authorization": f"Bearer {token_alice}"},
        json={"items": [{"product_id": "p1", "qty": 1}]}
    )
    assert alice_order.status_code == 201

    # Bob creates an order
    bob_order = client.post("/create_order",
        headers={"Authorization": f"Bearer {token_bob}"},
        json={"items": [{"product_id": "p2", "qty": 1}]}
    )
    assert bob_order.status_code == 201

    # Alice checks her orders - should only see 1 (hers)
    response = client.get("/orders",
        headers={"Authorization": f"Bearer {token_alice}"}
    )
    alice_orders = response.get_json()

    # This will FAIL if bug exists (Alice will see Bob's order too)
    assert len(alice_orders) == 1, \
        f"Alice should see only 1 order, but sees {len(alice_orders)} orders"
    assert alice_orders[0]["user"] == "alice", \
        "Alice should only see her own orders!"


@pytest.mark.skip(reason="Enable this test to check specific order access control")
def test_cannot_access_other_users_order():
    """
    BUG SCENARIO 2: Authorization Bypass - Direct Order Access

    Test that users cannot access other users' orders by order ID.

    TO TRIGGER THIS TEST FAILURE:
    In services/order-service/app.py, line 106, change:
        if o["order_id"] == order_id and o["user"] == username:
    To:
        if o["order_id"] == order_id:  # BUG: Doesn't check user ownership!

    Then remove @pytest.mark.skip from this test.
    """
    app = load_app()
    client = app.test_client()

    token_alice = get_test_token("alice")
    token_bob = get_test_token("bob")

    # Alice creates an order
    alice_response = client.post("/create_order",
        headers={"Authorization": f"Bearer {token_alice}"},
        json={"items": [{"product_id": "p1", "qty": 1}]}
    )
    alice_order = alice_response.get_json()
    alice_order_id = alice_order["order_id"]

    # Bob tries to access Alice's order
    bob_response = client.get(f"/orders/{alice_order_id}",
        headers={"Authorization": f"Bearer {token_bob}"}
    )

    # Should be denied (404 or 403)
    assert bob_response.status_code == 404, \
        "Bob should not be able to access Alice's order!"


@pytest.mark.skip(reason="Enable this test to check missing token handling")
def test_missing_token_rejected():
    """
    BUG SCENARIO 3: Missing Authentication

    Test that requests without authentication tokens are rejected.

    TO TRIGGER THIS TEST FAILURE:
    In services/order-service/app.py, line 57, change:
        if not auth.lower().startswith("bearer "):
    To:
        if False:  # BUG: Always allows access!

    Then remove @pytest.mark.skip from this test.
    """
    app = load_app()
    client = app.test_client()

    # Try to create order without token
    response = client.post("/create_order",
        json={"items": [{"product_id": "p1", "qty": 1}]}
    )

    # Should be rejected
    assert response.status_code == 401, "Missing token should be rejected!"
    assert "error" in response.get_json()


@pytest.mark.skip(reason="Enable this test to check malformed token handling")
def test_malformed_token_rejected():
    """
    BUG SCENARIO 4: Token Format Validation

    Test that malformed tokens are properly rejected.

    This should already pass with current code.
    """
    app = load_app()
    client = app.test_client()

    # Try with malformed authorization header
    response = client.post("/create_order",
        headers={"Authorization": "NotBearer xyz123"},
        json={"items": [{"product_id": "p1", "qty": 1}]}
    )

    # Should be rejected
    assert response.status_code == 401, "Malformed token should be rejected!"


@pytest.mark.skip(reason="Enable this test to check order list access control")
def test_order_list_requires_authentication():
    """
    BUG SCENARIO 5: Unauthenticated Access to Order List

    Test that accessing order list requires authentication.

    TO TRIGGER THIS TEST FAILURE:
    In services/order-service/app.py, line 114, change:
        if not auth.lower().startswith("bearer "):
    To:
        if False:  # BUG: Allows unauthenticated access!

    Then remove @pytest.mark.skip from this test.
    """
    app = load_app()
    client = app.test_client()

    # Try to list orders without authentication
    response = client.get("/orders")

    # Should be rejected
    assert response.status_code == 401, \
        "Accessing orders without authentication should be rejected!"
