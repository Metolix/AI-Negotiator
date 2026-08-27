# AI Police Negotiator Game

[![Live Demo](https://img.shields.io/badge/Live_Demo-game.metolix.dev-0070f3?style=for-the-badge&logo=google-chrome&logoColor=white)](https://game.metolix.dev)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Framework-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)

An interactive, AI driven crisis negotiation simulation. Players step into the shoes of a primary police negotiator attempting to de-escalate high stakes hostage situations through strategic dialogue, rapport building, and tactical empathy.

---

## Play the Live Demo

Experience the live application online:  
👉 **[https://game.metolix.dev](https://game.metolix.dev)**

> 🔒 **Testing Notice:** Access to the live environment is currently limited while the game undergoes active playtesting, balance updates, and model calibration.

---

## How It Works

The application bridges non-deterministic Large Language Models with a strictly deterministic Python game engine. Rather than allowing the AI to dictate the game state freely, the Python engine retains absolute authority over inventory, emotional variables, and scenario boundaries using the LLM purely for character immersion, intent recognition, and narrative synthesis.

### 1. Dynamic Emotional Matrix
Behind the scenes, the game engine tracks the suspect's hidden emotional profile across four key variables (0–100% scale):

| Variable | Description | Strategic Impact |
| :--- | :--- | :--- |
| **Trust** | Credibility of the negotiator's promises | Higher trust unlocks concessions and peaceful resolutions. |
| **Anger** | Agitation and volatility level | High anger drastically increases the risk of premature escalation. |
| **Fear** | Sense of being cornered | High fear triggers irrational counter demands or erratic behavior. |
| **Surrender Willingness** | Propensity to lay down weapons | Must reach critical thresholds to secure a surrender victory. |

---

### 2. The Core Execution Loop
1. **Player Dialogue Processing:** The negotiator's message is combined with scenario restrictions, available police resources, and recent transcript history.
2. **Delta Extraction:** High speed LLMs infer character emotion and propose mathematical adjustments (`trust_delta`, `anger_delta`, `fear_delta`, `surrender_delta`).
3. **Engine Validation:** The Python backend intercepts the AI's proposal. It enforces scenario boundaries, clamps variables between 0 and 100, updates hostage counts, and determines if win/loss conditions are met.
4. **Resolution Check:** The system checks if the situation ends via **Peaceful Surrender**, **All Hostages Released**, **Tactical Escalation**, or **Timeout (Max Turns Exceeded)**.

---

### 3. Resilient AI Orchestration

- **Multi-Model Fallback Cascade:** To ensure real time responsiveness and high availability, requests cycle seamlessly across models in the event of API rate limits or latency spikes.
- **Self-Healing JSON Engine:** If a model returns malformed structured data, an automated repair parser intervenes using a lightweight secondary model pass to restore valid schema formatting before updating state.
- **Context Window Management:** Manages conversational history with dynamic sliding-window summaries to keep token footprints low without forfeiting long-term memory.
- **In Game Telemetry:** Native support for operational commands like `/status` (inspect turn limits and demands) and `/history` (retrieve raw transcripts).

---

## Tech Stack

- **Backend:** Python 3.10+, Flask (Blueprints, REST API architecture)
- **AI Engine:** Groq API SDK (OpenAI-compatible protocol)

---

## 📜 License

This project is licensed under the **MIT License**. You are free to inspect, fork, and adapt the code for personal learning or portfolio demonstration, provided original copyright notices and author attributions remain intact.