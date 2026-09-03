import os
import secrets
import logging
from functools import wraps

from flask import Flask, render_template, request, redirect, jsonify, abort, session, g
from essentials import apis, syntax
from essentials import xero

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))

BACK_IMAGES = ["cool.jpg", "cool2.jpg", "cool3.jpg", "cool4.jpg"]
select_background = xero.ReplaceRandom(BACK_IMAGES)

_user_states = {}


def _get_state():
    sid = session.get("sid")
    if not sid:
        sid = secrets.token_hex(16)
        session["sid"] = sid
    if sid not in _user_states:
        _user_states[sid] = {
            "apikey": None,
            "api": None,
            "selected_api": None,
            "is_first_prompt": False,
        }
    return _user_states[sid]


def _init_api(state):
    if state["api"] is None and state["apikey"] and state["selected_api"]:
        try:
            state["api"] = apis.select_api[state["selected_api"]](apikey=state["apikey"])
        except Exception as e:
            logger.exception("Failed to initialise API client")
            state["apikey"] = None
            state["selected_api"] = None
            raise
    if state["api"] is not None and not state["is_first_prompt"]:
        try:
            state["api"].system_message(syntax.official_assistant_formatting_v1.FORMAT, False)
        except Exception as e:
            logger.exception("Failed to send system message")
            raise
        state["is_first_prompt"] = True


def _generate_csrf_token():
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)
    return session["_csrf_token"]


app.jinja_env.globals["csrf_token"] = _generate_csrf_token


def require_api(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        state = _get_state()
        if not state["apikey"]:
            return redirect("/login")
        try:
            _init_api(state)
        except Exception:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/req", methods=["POST"])
@require_api
def req():
    state = _get_state()
    if "request_messages" not in request.form:
        abort(400, description="Missing request_messages parameter.")
    try:
        return jsonify({str(i): v for i, v in enumerate(state["api"].get_formatted_messages())})
    except Exception as e:
        logger.exception("Failed to get messages")
        abort(500, description="Failed to retrieve messages.")


@app.route("/ajax", methods=["POST", "GET"])
@require_api
def ajax():
    state = _get_state()

    if request.method == "POST" and "newMessage" in request.form:
        csrf = request.form.get("_csrf_token")
        if not csrf or csrf != session.get("_csrf_token"):
            abort(403, description="Invalid CSRF token.")

        new_message = request.form["newMessage"]

        if new_message == "RESET_CHAT":
            try:
                state["api"] = apis.select_api[state["selected_api"]](apikey=state["apikey"])
                state["api"].system_message(syntax.official_assistant_formatting_v1.FORMAT, False)
                state["is_first_prompt"] = True
                return jsonify({"REFRESH": "TRUE"})
            except Exception as e:
                logger.exception("Failed to reset chat")
                abort(500, description="Failed to reset chat.")

        if new_message == "RESET_API":
            state["apikey"] = None
            state["api"] = None
            state["selected_api"] = None
            state["is_first_prompt"] = False
            return redirect("/login")

        try:
            state["api"].user_message(new_message)
        except Exception as e:
            logger.exception("Failed to send message")
            abort(502, description="Failed to get response from AI provider.")

        return jsonify({"successful": "true"})
    else:
        try:
            messages = state["api"].get_formatted_messages() if state["api"] else []
        except Exception:
            messages = []
        return render_template("ajax.html", messages=messages)


@app.route("/", methods=["POST", "GET"])
@require_api
def index():
    state = _get_state()

    if request.method == "POST":
        csrf = request.form.get("_csrf_token")
        if not csrf or csrf != session.get("_csrf_token"):
            abort(403, description="Invalid CSRF token.")

        new_message = request.form["newMessage"]

        if new_message == "RESET_CHAT":
            try:
                state["api"] = apis.select_api[state["selected_api"]](apikey=state["apikey"])
                state["api"].system_message(syntax.official_assistant_formatting_v1.FORMAT, False)
                state["is_first_prompt"] = True
            except Exception as e:
                logger.exception("Failed to reset chat")
            return redirect("/")

        if new_message == "RESET_API":
            state["apikey"] = None
            state["api"] = None
            state["selected_api"] = None
            state["is_first_prompt"] = False
            return redirect("/login")

        try:
            state["api"].user_message(new_message)
        except Exception as e:
            logger.exception("Failed to send message")
            abort(502, description="Failed to get response from AI provider.")

        return redirect("/")

    try:
        messages = state["api"].get_formatted_messages() if state["api"] else []
    except Exception:
        messages = []
    return render_template(
        "index.html",
        messages=messages,
        random_back=select_background.Next(),
    )


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        csrf = request.form.get("_csrf_token")
        if not csrf or csrf != session.get("_csrf_token"):
            abort(403, description="Invalid CSRF token.")

        apikey = request.form.get("apikey", "").strip()
        selected_api = request.form.get("apiplatform", "").strip()

        if not apikey or selected_api not in apis.select_api:
            abort(400, description="Invalid API key or platform selection.")

        state = _get_state()
        state["apikey"] = apikey
        state["selected_api"] = selected_api
        state["is_first_prompt"] = False
        state["api"] = None

        try:
            state["api"] = apis.select_api[selected_api](apikey=apikey)
            state["api"].system_message(syntax.official_assistant_formatting_v1.FORMAT, False)
            state["is_first_prompt"] = True
        except Exception as e:
            logger.exception("Failed to connect to API provider")
            state["apikey"] = None
            state["selected_api"] = None
            state["api"] = None
            abort(502, description="Failed to connect to API provider. Check your key and try again.")

        return redirect("/")
    return render_template("login.html")


@app.route("/test")
def test():
    return render_template("test.html")


if __name__ == "__main__":
    app.run(debug=False)
