"""
Business Logic Tests for Order Service Pricing

These tests check for pricing calculation and business rule bugs.
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


def get_test_token(username="testuser"):
    """Generate a test authentication token"""
    from itsdangerous import URLSafeSerializer
    signer = URLSafeSerializer("dev-secret", salt="user-auth")
    return signer.dumps({"u": username})


@pytest.mark.skip_disabled  # Test enabled
def test_order_total_calculation_with_quantity():
    """
    BUG SCENARIO 1: Price Calculation Error

    Test that order total is calculated correctly when ordering multiple quantities.

    TO TRIGGER THIS TEST FAILURE:
    In services/order-service/app.py, line 78, change:
        total = money(total + line_total)
    To:
        total = money(total + prod["price"])  # BUG: Should add line_total!

    Then remove @pytest.mark.skip from this test.
    """
    app = load_app()
    client = app.test_client()
    token = get_test_token()

    # Create order: 3 x Mouse ($19.99 each) = $59.97
    response = client.post("/create_order",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "items": [
                {"product_id": "p1", "qty": 3}  # 3 x $19.99 = $59.97
            ]
        }
    )

    assert response.status_code == 201
    order = response.get_json()

    # This will FAIL if bug exists (total will be $19.99 instead of $59.97)
    expected_total = 59.97
    actual_total = order["total"]
    assert actual_total == expected_total, \
        f"Order total incorrect: expected ${expected_total} but got ${actual_total}"


@pytest.mark.skip(reason="Enable this test to check multi-item order calculation")
def test_multi_item_order_total():
    """
    BUG SCENARIO 2: Multi-Item Calculation Error

    Test that order total is correct with multiple different items.

    Same bug as test_order_total_calculation_with_quantity
    """
    app = load_app()
    client = app.test_client()
    token = get_test_token()

    # Create order with multiple items:
    # 2 x Mouse ($19.99) = $39.98
    # 1 x Keyboard ($59.49) = $59.49
    # Total = $99.47
    response = client.post("/create_order",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "items": [
                {"product_id": "p1", "qty": 2},  # Mouse
                {"product_id": "p2", "qty": 1}   # Keyboard
            ]
        }
    )

    assert response.status_code == 201
    order = response.get_json()

    expected_total = 99.47
    actual_total = order["total"]
    assert actual_total == expected_total, \
        f"Multi-item order total incorrect: expected ${expected_total} but got ${actual_total}"


@pytest.mark.skip_disabled  # Test enabled
def test_negative_quantity_rejected():
    """
    BUG SCENARIO 3: Business Rule Violation - Negative Quantities

    Test that negative quantities are rejected.

    TO TRIGGER THIS TEST FAILURE:
    In services/order-service/app.py, line 75, change:
        if not prod or qty <= 0:
    To:
        if not prod:  # BUG: Removed qty check!

    Then remove @pytest.mark.skip from this test.
    """
    app = load_app()
    client = app.test_client()
    token = get_test_token()

    # Try to create order with negative quantity
    response = client.post("/create_order",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "items": [
                {"product_id": "p1", "qty": -5}  # Negative quantity!
            ]
        }
    )

    # Should be rejected
    assert response.status_code == 400, "Negative quantity should be rejected!"
    assert "error" in response.get_json()


@pytest.mark.skip(reason="Enable this test to check zero quantity validation")
def test_zero_quantity_rejected():
    """
    BUG SCENARIO 4: Business Rule Violation - Zero Quantities

    Test that zero quantities are rejected.

    Same bug as test_negative_quantity_rejected
    """
    app = load_app()
    client = app.test_client()
    token = get_test_token()

    # Try to create order with zero quantity
    response = client.post("/create_order",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "items": [
                {"product_id": "p1", "qty": 0}
            ]
        }
    )

    # Should be rejected
    assert response.status_code == 400, "Zero quantity should be rejected!"
    assert "error" in response.get_json()


@pytest.mark.skip(reason="Enable this test to check empty cart validation")
def test_empty_cart_rejected():
    """
    BUG SCENARIO 5: Empty Cart Allowed

    Test that orders with no items are rejected.

    TO TRIGGER THIS TEST FAILURE:
    In services/order-service/app.py, line 66-67, comment out:
        # if not items:
        #     return jsonify({"error":"items required"}), 400

    Then remove @pytest.mark.skip from this test.
    """
    app = load_app()
    client = app.test_client()
    token = get_test_token()

    # Try to create order with no items
    response = client.post("/create_order",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "items": []  # Empty cart
        }
    )

    # Should be rejected
    assert response.status_code == 400, "Empty cart should be rejected!"
    assert "error" in response.get_json()


@pytest.mark.skip(reason="Enable this test to check invalid product validation")
def test_invalid_product_rejected():
    """
    BUG SCENARIO 6: Invalid Product ID Handling

    Test that orders with non-existent products are rejected.

    This test should already pass with current code (good validation).
    Use it to verify validation is working.
    """
    app = load_app()
    client = app.test_client()
    token = get_test_token()

    # Try to order non-existent product
    response = client.post("/create_order",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "items": [
                {"product_id": "p999", "qty": 1}  # Doesn't exist
            ]
        }
    )

    # Should be rejected
    assert response.status_code == 400, "Invalid product should be rejected!"
    assert "error" in response.get_json()
