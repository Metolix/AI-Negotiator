# AI Police Negotiator Game

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

An interactive, AI driven crisis negotiation simulation. Players step into the shoes of a primary police negotiator attempting to de-escalate high stakes hostage situations through strategic dialogue, rapport building, and tactical empathy.

---

## Play the Live Demo

Experience the live application online:  
👉 **[https://game.metolix.dev](https://game.metolix.dev)**

> 🔒 **Testing Notice:** This game is under heavy testing. Errors may occur.

---

## Tech Stack

- **Backend:** Python 3.10+, Flask (Blueprints, REST API architecture)
- **AI Engine:** Groq API SDK (OpenAI-compatible protocol)

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

## Running Locally

You can run AI Police Negotiator locally on **Windows, macOS, or Linux**.

### Requirements

Before starting, make sure you have:

- **Python 3.10 or newer**
- **Git**
- A **Groq API key**

The project uses Flask for the web application and the required Python packages are listed in `requirements.txt`.

---

## 1. Clone the Repository

Open a terminal and clone the repository:

```bash
git clone https://github.com/Metolix/AI-Negotiator.git
cd AI-Negotiator
```

---

## 2. Create a Virtual Environment

A virtual environment keeps the project's dependencies isolated from the rest of your Python installation.

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

If you are using **PowerShell**:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

Once activated, you should see something similar to this in your terminal:

```text
(venv)
```

---

## 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

The project uses packages including:

- Flask
- OpenAI Python SDK
- python-dotenv

---

## 4. Get a Groq API Key

AI Police Negotiator uses **Groq** to generate the AI hostage-taker responses.

You will need your own Groq API key to run the AI locally.

### Create a Groq account

Go to:

https://console.groq.com/

Create an account or sign in.

### Create an API key

1. Open the **Groq Console**.
2. Go to **API Keys**.
3. Select **Create API Key**.
4. Give the key a name, such as `ai-negotiator-local`.
5. Create the key.
6. Copy the API key.

> **Keep your API key private. Do not share it or commit it to GitHub.**

You can manage your API keys here:

https://console.groq.com/keys

---

## 5. Environment Configuration Setup

Quick guide on copying environment template files (`.env.example`) to your local environment file (`.env`).

### Linux / macOS / Git Bash
```bash
cp .env.example .env
```

### Windows (Command Prompt)
```cmd
copy .env.example .env
```

### Windows (PowerShell)
```powershell
Copy-Item .env.example .env
# Shortcut / Alias:
cp .env.example .env
```

```env
GROQ_API_KEY=
GROQ_MODEL=qwen/qwen3.6-27b
MAX_TURNS=40
FLASK_SECRET_KEY=Random long string
TEST_PASS=123 #optional, see below
TEST_USER=user #optional, see below
```

Your project should look similar to:

```text
AI-Negotiator/
├── .env
├── app.py
├── ai_service.py
├── config.py
├── game_engine.py
├── routes.py
├── scenarios.json
├── requirements.txt
├── LICENSE
├── README.md
├── templates/
├── static/
└── ...
```

### Configure the values

Replace:

```text
your_groq_api_key_here
```

with the Groq API key you created.

For example:

```env
GROQ_API_KEY=gsk_your_actual_key_here
```

You should also change:

```env
FLASK_SECRET_KEY=change-this-to-a-random-secret
```

to a long random value.

Then configure the local testing login:

```env
TEST_USER=admin
TEST_PASS=change-this-password
```

For example:

```env
TEST_USER=admin
TEST_PASS=my-secure-local-password
```

The maximum number of turns can be configured with:

```env
MAX_TURNS=40
```

---

## 6. Protect Your API Key

**Do not put your Groq API key directly into the Python source code.**

Do not do this:

```python
GROQ_API_KEY = "gsk_your_api_key"
```

Instead, keep it in `.env`:

```env
GROQ_API_KEY=gsk_your_api_key
```

The application loads the value from the environment.

The repository's `.gitignore` already excludes `.env`, meaning your local environment file should not be committed to Git.

### Never commit this:

```text
.env
```

If you accidentally commit an API key, **revoke the key immediately** from the Groq Console and create a new one.

---

## 7. Start the Application

Make sure your virtual environment is activated.

Then run:

```bash
python app.py
```

The application should start on port `5000`.

Open your browser and go to:

```text
http://127.0.0.1:5000
```

You can also use:

```text
http://localhost:5000
```

---

## 8. Log In

The current application has Basic Authentication enabled for the testing environment.

When your browser asks for a username and password, use the values from your `.env` file.

For example:

```env
TEST_USER=admin
TEST_PASS=my-secure-local-password
```

Enter:

```text
Username: admin
Password: my-secure-local-password
```

> 🔒 **Notice:** To enable login (disabled by default), Un-comment all the lines in the routes.py file.

## Creating/Editing Scenarios

Scenarios are stored in:

```text
scenarios.json
```

You can add or modify scenarios by editing that file, provided they follow the expected scenario structure.

---

## 🔐 Security & Privacy

AI Police Negotiator is designed as a fictional simulation.

Do not enter real-world sensitive personal information into the simulator.

Negotiation messages may be transmitted to third-party AI providers, including Groq, in order to generate AI responses.

Do not use a real person's private information, credentials, API keys, or other sensitive information as game input.

For more information, see:

- [`Terms of Service`](templates/terms.html)
- [`Privacy Policy`](templates/privacy.html)

---

## 📜 License

AI Police Negotiator is released under the **MIT License**.

Copyright © 2026 **Sidhak Singh**

The MIT License allows you to:

- Use the software
- Copy the software
- Modify the software
- Merge the software
- Publish the software
- Distribute the software
- Sublicense the software
- Sell copies of the software

You must, however, retain the original copyright notice and license notice in copies or substantial portions of the software.

The full license is available in:

```text
LICENSE
```

If you fork, redistribute, or substantially reuse this project, please retain the original `LICENSE` file and copyright attribution.

---

## ⚠️ Disclaimer

AI Police Negotiator is a **fictional interactive simulation** created for roleplay, educational, and entertainment purposes.

All scenarios, characters, locations, incidents, and events depicted within the simulator are fictional.

The application does **not** represent official law-enforcement doctrine, emergency procedures, tactical guidance, or real-world operational protocols.

Do not treat the simulator's AI-generated responses as professional, legal, law-enforcement, emergency-response, or tactical advice.

The developer makes no guarantee regarding the accuracy, reliability, availability, or suitability of AI-generated content.

The application also relies on third-party AI infrastructure. Service availability and AI responses may therefore depend on external providers.

---

## ❤️ Credits

Created by **Sidhak Singh (Metolix)**.

GitHub:

https://github.com/Metolix

AI functionality powered by **Groq**.
