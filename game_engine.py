import json
from copy import deepcopy
from config import MAX_TURNS, SCENARIOS_FILE


def clamp(value, low=0, high=100):
    return max(low, min(high, int(value)))


def load_scenarios():
    if not SCENARIOS_FILE.exists():
        raise FileNotFoundError(f"Could not find {SCENARIOS_FILE.name}")

    with open(SCENARIOS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def initialize_state(scenario):
    state = deepcopy(scenario["state"])
    state["turn"] = 0
    state["max_turns"] = MAX_TURNS
    state["conversation_summary"] = []
    return state


def create_game(scenario):
    return {
        "scenario": deepcopy(scenario),
        "state": initialize_state(scenario),
        "history": [
            {
                "speaker": scenario["character"]["name"],
                "text": scenario["opening"],
            }
        ],
        "finished": False,
        "ending": None,
    }


def apply_ai_result(scenario, state, result):
    state["trust"] = clamp(state["trust"] + int(result.get("trust_delta", 0)))
    state["anger"] = clamp(state["anger"] + int(result.get("anger_delta", 0)))
    state["fear"] = clamp(state["fear"] + int(result.get("fear_delta", 0)))
    state["surrender_willingness"] = clamp(
        state["surrender_willingness"] + int(result.get("surrender_delta", 0))
    )

    release_count = max(0, min(1, int(result.get("hostages_released", 0))))

    if result.get("action") == "release_hostage":
        release_count = 1

    if release_count:
        state["hostages"] = max(0, state["hostages"] - release_count)

    demand_change = str(result.get("demand_change", "")).strip()

    if demand_change:
        existing = {demand.lower() for demand in state["demands"]}
        if demand_change.lower() not in existing:
            state["demands"].append(demand_change)

    action = result.get("action", "continue")

    valid_surrender = state["surrender_willingness"] >= 80 or (
        action == "surrender" and state["trust"] >= 65
    )

    if action == "surrender" and not valid_surrender:
        action = "continue"

    return action, valid_surrender


def determine_ending(action, valid_surrender, state):
    if action == "surrender" and valid_surrender:
        score = 100 + state["hostages"] * 10 + state["trust"] - state["anger"]
        return {
            "type": "surrender",
            "title": "SUSPECT SURRENDERED",
            "message": "The suspect stood down and surrendered.",
            "score": score,
        }

    if state["hostages"] <= 0:
        score = 100 + state["trust"] - state["anger"]
        return {
            "type": "all_released",
            "title": "ALL HOSTAGES SAFELY EXTRACTED",
            "message": "All hostages have been safely released.",
            "score": score,
        }

    if action == "escalate":
        score = max(0, 40 + state["hostages"] * 5 - state["anger"])
        return {
            "type": "escalate",
            "title": "SITUATION ESCALATED",
            "message": "The negotiation has broken down and the situation has escalated.",
            "score": score,
        }

    if state["turn"] >= state["max_turns"]:
        score = max(
            0, 50 + state["hostages"] * 5 + state["trust"] - state["anger"]
        )
        return {
            "type": "timeout",
            "title": "NEGOTIATION TIMED OUT",
            "message": "The maximum number of negotiation turns has been reached.",
            "score": score,
        }

    return None