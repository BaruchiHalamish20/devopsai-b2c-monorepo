from flask import Flask, request, jsonify, redirect, url_for
from itsdangerous import URLSafeSerializer
import hashlib, os
from prometheus_client import generate_latest, Counter, Histogram, start_http_server

app = Flask(__name__)
SECRET = os.getenv("SECRET_KEY", "dev-secret")
signer = URLSafeSerializer(SECRET, salt="user-auth")
ENVIRONMENT = os.getenv("APP_ENV", "unknown")  # set via Helm values per env

# Prometheus Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status_code'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Latency', ['method', 'endpoint'])
# Custom metric example
USER_REGISTRATIONS = Counter('user_registrations_total', 'Total number of user registrations')

USERS = {}
NEXT_ID = 1

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def make_token(username: str) -> str:
    return signer.dumps({"u": username})

def parse_token(token: str):
    try:
        data = signer.loads(token)
        return data.get("u")
    except Exception:
        return None

@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok", "service": "user-service", "env": ENVIRONMENT})

@app.get("/env")
def env():
    return jsonify({"env": ENVIRONMENT})

@app.post("/register")
def register():
    global NEXT_ID
    payload = request.get_json(force=True, silent=True) or {}
    username = payload.get("username", "").strip()
    password = payload.get("password", "")
    name = payload.get("name", "").strip()
    email = payload.get("email", "").strip()

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400
    if username in USERS:
        return jsonify({"error": "username already exists"}), 409

    user = {
        "id": str(NEXT_ID),
        "username": username,
        "name": name,
        "email": email,
        "password_hash": hash_pw(password)
    }
    USERS[username] = user
    NEXT_ID += 1
    public = {k: v for k, v in user.items() if k != "password_hash"}
    USER_REGISTRATIONS.inc() # Increment custom metric on successful registration
    return jsonify(public), 201

@app.post("/login")
def login():
    payload = request.get_json(force=True, silent=True) or {}
    username = payload.get("username", "").strip()
    password = payload.get("password", "")
    user = USERS.get(username)
    if not user or user["password_hash"] != hash_pw(password):
        return jsonify({"error": "invalid credentials"}), 401
    token = make_token(username)
    return jsonify({"token": token})

@app.get("/profile")
def profile():
    auth = request.headers.get("authorization", "")
    if not auth.lower().startswith("bearer "):
        return jsonify({"error": "missing bearer token"}), 401
    token = auth.split(" ", 1)[1].strip()
    username = parse_token(token)
    if not username or username not in USERS:
        return jsonify({"error": "invalid token"}), 401
    user = USERS[username]
    public = {k: v for k, v in user.items() if k != "password_hash"}
    return jsonify(public)

@app.get("/baruchi-login")
def baruchi_login():
    """Shortcut route that auto-creates 'baruchi' and redirects to profile."""
    global NEXT_ID

    # create user if not exists
    if "baruchi" not in USERS:
        USERS["baruchi"] = {
            "id": str(NEXT_ID),
            "username": "baruchi",
            "name": "Baruchi Halamish",
            "email": "baruchi@example.com",
            "password_hash": hash_pw("devopsai")
        }
        NEXT_ID += 1

    # generate token and redirect to profile
    token = make_token("baruchi")
    profile_url = url_for("profile", _external=True)
    # attach token as query param for browser-friendly redirection
    return redirect(f"{profile_url}?token={token}")

@app.get("/niv-login")
def niv_login():
    return jsonify({"who is the king?": "Niv"})

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': 'text/plain; version=0.0.4; charset=utf-8'}

if __name__ == "__main__":
    # Start up the Prometheus client
    start_http_server(8000)

    app.run(host="0.0.0.0", port=5000)
