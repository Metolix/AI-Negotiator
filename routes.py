import random
from copy import deepcopy
from flask import Blueprint, jsonify, render_template, request, session, Response

from config import TEST_USER, TEST_PASS
from ai_service import get_client, call_ai
from game_engine import (
    load_scenarios,
    create_game,
    apply_ai_result,
    determine_ending,
)

routes = Blueprint("routes", __name__)


# Helpers & Session Management

def save_game(game):
    if len(game.get("history", [])) > 15:
        game["history"] = game["history"][-15:]
    session["game"] = game
    session.modified = True


def get_game():
    return session.get("game")


def check_auth(username, password):
    return username == TEST_USER and password == TEST_PASS


def authenticate():
    return Response(
        "Authentication required to access this testing environment.",
        401,
        {"WWW-Authenticate": 'Basic realm="Testing Environment"'},
    )


@routes.before_request
def require_auth():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()


# Endpoint Handlers

@routes.route("/")
def index():
    return render_template("index.html")

@routes.route('/terms')
def terms():
    return render_template('terms.html')

@routes.route('/privacy')
def privacy():
    return render_template('privacy.html')


@routes.route("/api/scenarios")
def scenarios():
    data = load_scenarios()
    return jsonify([
        {
            "id": index,
            "name": scenario["name"],
            "description": scenario["description"],
            "location": scenario["location"],
        }
        for index, scenario in enumerate(data)
    ])


@routes.route("/api/new", methods=["POST"])
def new_game():
    scenarios = load_scenarios()
    data = request.get_json(silent=True) or {}
    scenario_id = data.get("scenario")

    if scenario_id == "random":
        scenario = deepcopy(random.choice(scenarios))
    else:
        try:
            scenario_index = int(scenario_id)
            scenario = deepcopy(scenarios[scenario_index])
        except (ValueError, TypeError, IndexError):
            return jsonify({"error": "Invalid scenario."}), 400

    game = create_game(scenario)
    save_game(game)

    return jsonify({
        "success": True,
        "scenario": game["scenario"],
        "state": game["state"],
        "history": game["history"],
    })


@routes.route("/api/game")
def current_game():
    game = get_game()
    if not game:
        return jsonify({"game": None})

    return jsonify({
        "game": {
            "scenario": game["scenario"],
            "state": game["state"],
            "history": game["history"],
            "finished": game["finished"],
            "ending": game["ending"],
        }
    })


@routes.route("/api/message", methods=["POST"])
def message():
    game = get_game()

    if not game:
        return jsonify({"error": "No active game."}), 400

    if game["finished"]:
        return jsonify({"error": "This negotiation has already ended."}), 400

    data = request.get_json(silent=True) or {}
    player_message = str(data.get("message", "")).strip()

    if not player_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    # Commands
    if player_message.lower() == "/status":
        state = game["state"]
        return jsonify({
            "type": "status",
            "state": {
                "hostages": state["hostages"],
                "initial_hostages": state["initial_hostages"],
                "turn": state["turn"],
                "max_turns": state["max_turns"],
                "demands": state["demands"],
            },
        })

    if player_message.lower() == "/history":
        return jsonify({
            "type": "history",
            "history": game["history"],
        })

    state = game["state"]
    scenario = game["scenario"]
    history = game["history"]

    state["turn"] += 1
    history.append({
        "speaker": "Negotiator",
        "text": player_message,
    })

    try:
        client = get_client()
        result = call_ai(client, scenario, state, history, player_message)
    except Exception as error:
        state["turn"] -= 1
        if history:
            history.pop()

        return jsonify({
            "error": "AI communication failed. Please try again.",
            "details": str(error),
        }), 500

    action, valid_surrender = apply_ai_result(scenario, state, result)
    dialogue = str(result.get("dialogue", "..."))

    history.append({
        "speaker": scenario["character"]["name"],
        "text": dialogue,
    })

    state["conversation_summary"].append(
        f"Turn {state['turn']}: Negotiator said: {player_message[:180]}. Hostage-taker action: {action}."
    )
    state["conversation_summary"] = state["conversation_summary"][-20:]

    ending = determine_ending(action, valid_surrender, state)

    if ending:
        ending["score"] = max(0, min(200, int(ending["score"])))
        game["finished"] = True
        game["ending"] = ending

    save_game(game)

    return jsonify({
        "type": "response",
        "dialogue": dialogue,
        "action": action,
        "state": state,
        "ending": ending,
    })


@routes.route("/api/reset", methods=["POST"])
def reset():
    session.pop("game", None)
    return jsonify({"success": True})