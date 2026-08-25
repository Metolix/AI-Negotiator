import os
import secrets
import time
from functools import wraps
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from game_engine import GameEngine, load_scenarios

load_dotenv()

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
    MAX_CONTENT_LENGTH=16 * 1024,
)

# Store only a password hash. Generate one with:
# python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-password'))"
ACCESS_PASSWORD_HASH = os.environ.get("ACCESS_PASSWORD_HASH", "")
LOGIN_WINDOW = 300
MAX_LOGIN_ATTEMPTS = 8
login_attempts = {}


def authenticated(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def csrf_ok():
    token = session.get("csrf_token")
    supplied = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token")
    return bool(token and supplied and secrets.compare_digest(token, supplied))


@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; "
        "connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    )
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("authenticated"):
        return redirect(url_for("index"))
    error = None
    if request.method == "POST":
        ip = request.remote_addr or "unknown"
        now = time.time()
        recent = [t for t in login_attempts.get(ip, []) if now - t < LOGIN_WINDOW]
        login_attempts[ip] = recent
        if len(recent) >= MAX_LOGIN_ATTEMPTS:
            error = "Too many attempts. Try again later."
        elif not ACCESS_PASSWORD_HASH:
            error = "Access password is not configured on the server."
        else:
            login_attempts[ip].append(now)
            password = request.form.get("password", "")
            if check_password_hash(ACCESS_PASSWORD_HASH, password):
                session.clear()
                session["authenticated"] = True
                session["csrf_token"] = secrets.token_urlsafe(32)
                session["session_nonce"] = secrets.token_urlsafe(16)
                return redirect(url_for("index"))
            error = "Invalid access credentials."
    return render_template("login.html", error=error)


@app.post("/logout")
def logout():
    if not csrf_ok():
        return "Forbidden", 403
    session.clear()
    return redirect(url_for("login"))


@app.get("/")
@authenticated
def index():
    scenarios = load_scenarios()
    return render_template("index.html", scenarios=scenarios, csrf_token=session["csrf_token"])


@app.post("/api/start")
@authenticated
def start():
    if not csrf_ok():
        return jsonify(error="Forbidden"), 403
    data = request.get_json(silent=True) or {}
    scenario_id = str(data.get("scenario_id", "")).strip()
    difficulty = str(data.get("difficulty", "standard")).strip().lower()
    scenarios = load_scenarios()
    scenario = next((s for s in scenarios if s["id"] == scenario_id), None)
    if not scenario:
        return jsonify(error="Unknown scenario"), 404
    if difficulty not in scenario["difficulties"]:
        return jsonify(error="Unknown difficulty"), 400
    engine = GameEngine(scenario, difficulty)
    session["game"] = engine.export_state()
    return jsonify(engine.public_state())


@app.post("/api/message")
@authenticated
def message():
    if not csrf_ok():
        return jsonify(error="Forbidden"), 403
    data = request.get_json(silent=True) or {}
    text = str(data.get("message", "")).strip()
    if not text or len(text) > 2000:
        return jsonify(error="Message must be 1-2000 characters."), 400
    saved = session.get("game")
    if not saved:
        return jsonify(error="No active scenario."), 400
    engine = GameEngine.from_state(saved)
    result = engine.player_turn(text)
    session["game"] = engine.export_state()
    return jsonify(result)


@app.post("/api/ert")
@authenticated
def ert():
    if not csrf_ok():
        return jsonify(error="Forbidden"), 403
    saved = session.get("game")
    if not saved:
        return jsonify(error="No active scenario."), 400
    engine = GameEngine.from_state(saved)
    result = engine.request_ert_breach()
    session["game"] = engine.export_state()
    return jsonify(result)


@app.get("/api/state")
@authenticated
def state():
    saved = session.get("game")
    if not saved:
        return jsonify(active=False)
    return jsonify(active=True, **GameEngine.from_state(saved).public_state())


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
