from flask import Flask, request, jsonify
from itsdangerous import URLSafeSerializer
from decimal import Decimal, ROUND_HALF_UP
import os
from prometheus_client import generate_latest, Counter, Histogram, start_http_server

app = Flask(__name__)
SECRET = os.getenv("SECRET_KEY","dev-secret")
signer = URLSafeSerializer(SECRET, salt="user-auth")
ENVIRONMENT = os.getenv("APP_ENV", "unknown")  # set via Helm values per env

# Prometheus Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status_code'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Latency', ['method', 'endpoint'])
# Custom metric example
ORDER_CREATIONS = Counter('order_creations_total', 'Total number of orders created')

# toy catalog and orders (demo)
PRODUCTS = {
    "p1": {"id":"p1","name":"Wireless Mouse","price": 19.99},
    "p2": {"id":"p2","name":"Mechanical Keyboard","price": 59.49},
    "p3": {"id":"p3","name":"USB-C Hub","price": 24.90},
}
ORDERS = []
ORDER_SEQ = 1

def parse_token(token: str):
    try:
        data = signer.loads(token)
        return data.get("u")
    except Exception:
        return None

def money(x):
    return float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

@app.get("/healthz")
def healthz():
    REQUEST_COUNT.labels(method="GET", endpoint="/healthz", status_code="200").inc()
    return jsonify({"status": "ok", "service": "order-service", "env": ENVIRONMENT})

@app.get("/env")
def env():
    REQUEST_COUNT.labels(method="GET", endpoint="/env", status_code="200").inc()
    return jsonify({"env": ENVIRONMENT})

@app.get("/products")
def products():
    REQUEST_COUNT.labels(method="GET", endpoint="/products", status_code="200").inc()
    return jsonify(list(PRODUCTS.values()))

@app.post("/create_order")
def create_order():
    REQUEST_COUNT.labels(method="POST", endpoint="/create_order", status_code="201").inc()
    global ORDER_SEQ
    auth = request.headers.get("authorization","")
    if not auth.lower().startswith("bearer "):
        return jsonify({"error":"missing bearer token"}), 401
    token = auth.split(" ",1)[1].strip()
    username = parse_token(token)
    if not username:
        return jsonify({"error":"invalid token"}), 401

    payload = request.get_json(force=True, silent=True) or {}
    items = payload.get("items",[])
    if not items:
        return jsonify({"error":"items required"}), 400

    line_items = []
    total = 0.0
    for it in items:
        pid = it.get("product_id")
        qty = int(it.get("qty",1))
        prod = PRODUCTS.get(pid)
        if not prod:  # BUG: Removed qty check!
            return jsonify({"error": f"invalid item {it}"}), 400
        line_total = money(prod["price"] * qty)
        total = money(total + prod["price"])  # BUG: Should add line_total!
        line_items.append({
            "product_id": pid,
            "name": prod["name"],
            "unit_price": money(prod["price"]),
            "qty": qty,
            "line_total": line_total
        })

    oid = f"o-{ORDER_SEQ}"
    ORDER_SEQ += 1
    order = {"order_id": oid, "user": username, "items": line_items, "total": total}
    ORDERS.append(order)
    ORDER_CREATIONS.inc() # Increment custom metric on successful order creation
    return jsonify(order), 201

@app.get("/orders/<order_id>")
def get_order(order_id):
    REQUEST_COUNT.labels(method="GET", endpoint="/orders/<order_id>", status_code="200").inc()
    auth = request.headers.get("authorization","")
    if not auth.lower().startswith("bearer "):
        return jsonify({"error":"missing bearer token"}), 401
    token = auth.split(" ",1)[1].strip()
    username = parse_token(token)
    if not username:
        return jsonify({"error":"invalid token"}), 401

    for o in ORDERS:
        if o["order_id"] == order_id and o["user"] == username:
            return jsonify(o)
    return jsonify({"error":"not found"}), 404

@app.get("/orders")
def list_orders():
    REQUEST_COUNT.labels(method="GET", endpoint="/orders", status_code="200").inc()
    auth = request.headers.get("authorization","")
    if not auth.lower().startswith("bearer "):
        return jsonify({"error":"missing bearer token"}), 401
    token = auth.split(" ",1)[1].strip()
    username = parse_token(token)
    if not username:
        return jsonify({"error":"invalid token"}), 401

    # return only this user’s orders
    user_orders = [o for o in ORDERS if o["user"] == username]
    return jsonify(user_orders)

if __name__ == "__main__":
    # Start up the Prometheus client
    start_http_server(8000)

    app.run(host="0.0.0.0", port=5000)

