const $ = (selector) => document.querySelector(selector);
const selection = $("#selection");
const game = $("#game");
const messages = $("#messages");
let current = null;
let busy = false;

const difficultyNotes = {
  tutorial: "Guided pace, forgiving reactions and a generous turn budget.",
  easy: "The NPC is cooperative and small mistakes are recoverable.",
  standard: "Balanced reactions. Consistency and rapport matter.",
  hard: "The NPC notices contradictions and reacts sharply to mistakes.",
  extreme: "Low forgiveness, volatile emotions and a narrow path to resolution."
};

document.querySelectorAll("select[data-scenario]").forEach((select) => {
  const note = document.querySelector(`[data-note-for="${select.dataset.scenario}"]`);
  const update = () => { if (note) note.textContent = difficultyNotes[select.value] || "Difficulty changes NPC behavior and the available time."; };
  select.addEventListener("change", update);
  update();
});

async function post(url, body = {}) {
  const response = await fetch(url, {
    method: "POST",
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", "X-CSRF-Token": window.CSRF || "" },
    body: JSON.stringify(body)
  });
  let data = {};
  try { data = await response.json(); } catch (_) { data = { error: `Server returned HTTP ${response.status}.` }; }
  if (!response.ok && !data.error) data.error = `Request failed (${response.status}).`;
  return data;
}

function addMessage(speaker, text, event = "") {
  const d = document.createElement("article");
  const isPlayer = speaker === "Negotiator";
  d.className = `msg ${isPlayer ? "player" : "suspect"}`;
  const who = document.createElement("div"); who.className = "who"; who.textContent = speaker;
  const bubble = document.createElement("div"); bubble.className = "bubble"; bubble.textContent = text;
  d.append(who, bubble);
  if (event && event !== "none") { const tag = document.createElement("span"); tag.className = "event-tag"; tag.textContent = event.replaceAll("_", " "); d.append(tag); }
  messages.appendChild(d);
  messages.scrollTop = messages.scrollHeight;
}

function setBar(id, value) {
  const bar = $(`#${id}-bar`);
  if (bar) bar.style.width = `${Math.max(0, Math.min(100, Number(value) || 0))}%`;
}

function render(state) {
  current = state;
  const s = state.state;
  $("#game-name").textContent = state.scenario.name;
  $("#game-location").textContent = state.scenario.location;
  $("#game-difficulty").textContent = (state.difficulty_info?.label || state.difficulty || "standard").toUpperCase();
  $("#hostages").textContent = `${s.hostages}/${s.initial_hostages}`;
  $("#hostage-note").textContent = s.hostages === 0 ? "Everyone accounted for" : `${s.hostages} still inside`;
  $("#turn").textContent = `${s.turn}/${s.max_turns}`;
  $("#turn-label").textContent = `TURN ${s.turn} / ${s.max_turns}`;
  $("#score").textContent = s.score ?? 0;
  $("#trust").textContent = s.trust;
  $("#anger").textContent = s.anger;
  $("#surrender").textContent = s.surrender_willingness;
  $("#quality").textContent = (s.negotiation_quality || "Unrated").toUpperCase();
  setBar("trust", s.trust); setBar("anger", s.anger); setBar("surrender", s.surrender_willingness);
  $("#event").innerHTML = `<span class="event-dot"></span>${s.event && s.event !== "none" ? s.event.replaceAll("_", " ") : "No incident event."}`;
  const demands = $("#demands"); demands.innerHTML = "";
  (s.demands || []).forEach((d) => { const li = document.createElement("li"); li.textContent = d; demands.appendChild(li); });
  $("#ert").disabled = !!s.outcome || !s.ert_available;
  if (s.outcome) {
    const labels = { surrender: "SUSPECT SURRENDERED", hostages_safe: "HOSTAGES SAFELY RELEASED", timeout: "NEGOTIATION TIMED OUT", ert_controlled: "SCENE RESOLVED — NO SIMULATED FATALITIES", ert_controlled_with_casualties: "SCENE RESOLVED — SIMULATED FATALITIES" };
    $("#ending").classList.remove("hidden");
    $("#ending").textContent = labels[s.outcome] || "SCENE RESOLVED";
    $("#composer").classList.add("hidden");
  } else {
    $("#ending").classList.add("hidden");
    $("#composer").classList.remove("hidden");
  }
}

function showError(message) {
  const box = $("#system-error"); box.textContent = message || "Something went wrong."; box.classList.remove("hidden");
}
function clearError() { $("#system-error").classList.add("hidden"); }
function setBusy(value) {
  busy = value;
  $("#send").disabled = value;
  $("#message").disabled = value;
  $("#typing").classList.toggle("hidden", !value);
}

async function startIncident(button) {
  if (busy) return;
  clearError();
  const id = button.dataset.start;
  const select = document.querySelector(`select[data-scenario="${id}"]`);
  button.disabled = true;
  const result = await post("/api/start", { scenario_id: id, difficulty: select?.value || "standard" });
  button.disabled = false;
  if (result.error) { showError(result.error); return; }
  selection.classList.add("hidden"); game.classList.remove("hidden"); messages.innerHTML = "";
  (result.history || []).forEach((m) => addMessage(m.speaker, m.text, m.event));
  render(result);
}

document.querySelectorAll("[data-start]").forEach((button) => button.addEventListener("click", () => startIncident(button)));

$("#composer").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (busy) return;
  const box = $("#message"); const text = box.value.trim(); if (!text) return;
  clearError(); addMessage("Negotiator", text); box.value = ""; setBusy(true);
  const result = await post("/api/message", { message: text });
  setBusy(false);
  if (result.error) { showError(result.error); return; }
  if (result.last_dialogue) addMessage(current?.scenario?.character || "Suspect", result.last_dialogue, result.state?.event);
  render(result);
  box.focus();
});

$("#ert").addEventListener("click", async () => {
  if (busy || !confirm("Request abstract ERT resolution? This is a fictional game outcome and can produce simulated fatalities.")) return;
  clearError(); setBusy(true);
  const result = await post("/api/ert");
  setBusy(false);
  if (result.error) { showError(result.error); return; }
  if (result.ert_result) addMessage("INCIDENT COMMAND", result.ert_result, "ert_resolution");
  render(result);
});

$("#back").addEventListener("click", () => {
  if (!confirm("End this session and return to incident selection?")) return;
  game.classList.add("hidden"); selection.classList.remove("hidden"); messages.innerHTML = ""; current = null;
});

$("#message").addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); $("#composer").requestSubmit(); }
});

fetch("/api/state", { credentials: "same-origin" }).then(r => r.ok ? r.json() : null).then(data => {
  if (data?.active) { selection.classList.add("hidden"); game.classList.remove("hidden"); (data.history || []).forEach(m => addMessage(m.speaker, m.text, m.event)); render(data); }
}).catch(() => {});
