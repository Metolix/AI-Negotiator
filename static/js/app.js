let game = null;

async function loadScenarios() {
    const response = await fetch("/api/scenarios");
    const scenarios = await response.json();
    const grid = document.getElementById("scenarioGrid");

    grid.innerHTML = "";

    scenarios.forEach(scenario => {
        const card = document.createElement("div");
        card.className = "scenario";
        card.innerHTML = `
            <h3>[${scenario.id + 1}] ${escapeHtml(scenario.name)}</h3>
            <p>${escapeHtml(scenario.description)}</p>
            <p>LOCATION: ${escapeHtml(scenario.location)}</p>
            <button>DEPLOY</button>
        `;
        card.addEventListener("click", () => startGame(scenario.id));
        grid.appendChild(card);
    });
}

async function startGame(scenario) {
    const response = await fetch("/api/new", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario: scenario })
    });
    const data = await response.json();

    if (!response.ok) {
        alert(data.error || "Unable to start game.");
        return;
    }
    game = data;
    showGame();
}

async function startRandom() {
    await startGame("random");
}

function showGame() {
    document.getElementById("selectionScreen").classList.add("hidden");
    document.getElementById("gameScreen").classList.remove("hidden");

    const scenario = game.scenario;
    document.getElementById("incident").textContent = "INCIDENT: " + scenario.name.toUpperCase();
    document.getElementById("location").textContent = "Location: " + scenario.location;
    document.getElementById("description").textContent = scenario.description;

    renderTranscript();
    updateStatus();
}

function renderTranscript() {
    const transcript = document.getElementById("transcript");
    transcript.innerHTML = "";
    game.history.forEach(item => addMessage(item.speaker, item.text, false));
}

function addMessage(speaker, text, scroll = true) {
    const transcript = document.getElementById("transcript");
    const message = document.createElement("div");
    message.className = "message";
    const speakerClass = speaker === "Negotiator" ? "negotiator" : "hostage";

    message.innerHTML = `
        <span class="${speakerClass}">${escapeHtml(speaker)}:</span>
        ${escapeHtml(text)}
    `;
    transcript.appendChild(message);

    if (scroll) {
        transcript.scrollTop = transcript.scrollHeight;
    }
}

function updateStatus() {
    const state = game.state;
    document.getElementById("hostages").textContent = `${state.hostages}/${state.initial_hostages}`;
    document.getElementById("turn").textContent = `${state.turn}/${state.max_turns}`;
    document.getElementById("demands").textContent = state.demands.length ? state.demands.join(", ") : "None";
}

async function sendMessage() {
    const input = document.getElementById("messageInput");
    const message = input.value.trim();
    if (!message) return;

    const sendButton = document.getElementById("sendButton");
    input.value = "";
    sendButton.disabled = true;
    sendButton.textContent = "...";

    addMessage("Negotiator", message);

    try {
        const response = await fetch("/api/message", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message })
        });
        const data = await response.json();

        if (!response.ok) {
            addMessage("SYSTEM", data.error || "An error occurred.");
            return;
        }

        if (data.type === "status") {
            addMessage("COMMANDER", JSON.stringify(data.state, null, 2));
            return;
        }

        if (data.type === "history") {
            renderTranscript();
            return;
        }

        game.state = data.state;
        game.history.push({
            speaker: game.scenario.character.name,
            text: data.dialogue
        });

        addMessage(game.scenario.character.name, data.dialogue);
        updateStatus();

        if (data.ending) {
            showEnding(data.ending);
        }
    } catch (error) {
        addMessage("SYSTEM", "Connection to command server failed.");
    } finally {
        sendButton.disabled = false;
        sendButton.textContent = "SEND";
        input.focus();
    }
}

function showEnding(ending) {
    const box = document.getElementById("ending");
    box.classList.remove("hidden");

    document.getElementById("endingTitle").textContent = ending.title;
    document.getElementById("endingMessage").textContent = ending.message;
    document.getElementById("score").textContent = `PERFORMANCE RATING: ${ending.score} / 200`;
    document.getElementById("inputArea").classList.add("hidden");
}

async function newOperation() {
    await fetch("/api/reset", { method: "POST" });
    location.reload();
}

function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = String(value);
    return div.innerHTML;
}

document.addEventListener("DOMContentLoaded", () => {
    const messageInput = document.getElementById("messageInput");
    if (messageInput) {
        messageInput.addEventListener("keydown", event => {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        });
        loadScenarios();
    }
});