const API = "http://localhost:8000/api";
let chatHistory = [];

// Tabs
document.querySelectorAll(".nav-tab").forEach(tab => {
  tab.onclick = () => {
    document.querySelectorAll(".nav-tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById(tab.dataset.tab).classList.add("active");
    if (tab.dataset.tab === "track") loadAllComplaints();
  };
});

// CHAT
async function sendChat() {
  const input = document.getElementById("chatInput");
  const msg = input.value.trim();
  if (!msg) return;
  addMsg(msg, "user");
  input.value = "";
  addMsg("⏳ Thinking...", "bot", true);

  try {
    const res = await fetch(`${API}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg, history: chatHistory })
    });
    const data = await res.json();
    removeThinking();
    addMsg(data.reply, "bot");
    chatHistory.push({ role: "user", parts: [msg] });
    chatHistory.push({ role: "model", parts: [data.reply] });
  } catch (e) {
    removeThinking();
    addMsg("⚠️ Server error. Is backend running on port 8000?", "bot");
  }
}
function addMsg(text, cls, isThinking = false) {
  const box = document.getElementById("chatBox");
  const div = document.createElement("div");
  div.className = "msg " + cls + (isThinking ? " thinking" : "");
  if (isThinking) div.id = "thinking";
  
  const avatar = cls === "user" ? "👤" : "🇮🇳";
  const name = cls === "user" ? "You" : 'Bharat Mitra <span class="verified">✓ Verified AI</span>';
  
  div.innerHTML = `
    <div class="avatar">${avatar}</div>
    <div class="msg-content">
      <div class="msg-name">${name}</div>
      ${isThinking ? '' : escapeHtml(text)}
    </div>
  `;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML.replace(/\n/g, '<br/>');
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML.replace(/\n/g, '<br/>');
}
function removeThinking() { document.getElementById("thinking")?.remove(); }
function quickAsk(q) { document.getElementById("chatInput").value = q; sendChat(); }
document.getElementById("chatInput").addEventListener("keypress", e => { if (e.key === "Enter") sendChat(); });

// REPORT ISSUE
document.getElementById("reportForm").onsubmit = async (e) => {
  e.preventDefault();
  const resultDiv = document.getElementById("reportResult");
  resultDiv.textContent = "⏳ Analyzing image with Gemini Vision...";

  const fd = new FormData();
  fd.append("user_name", document.getElementById("userName").value);
  fd.append("description", document.getElementById("issueDesc").value);
  fd.append("location", document.getElementById("location").value);
  fd.append("image", document.getElementById("issueImage").files[0]);

  try {
    const res = await fetch(`${API}/report-issue`, { method: "POST", body: fd });
    const data = await res.json();
    resultDiv.innerHTML = `
      <div class="complaint-card">
        <h3>✅ Complaint Filed!</h3>
        <p><b>ID:</b> ${data.complaint.id}</p>
        <p><b>Status:</b> <span class="status">${data.complaint.status}</span></p>
        <p><b>ETA:</b> ${data.complaint.eta}</p>
        <h4>🤖 AI Analysis:</h4>
        <pre>${data.ai_analysis}</pre>
      </div>`;
  } catch { resultDiv.textContent = "⚠️ Failed to submit."; }
};

// SCHEMES
document.getElementById("schemeForm").onsubmit = async (e) => {
  e.preventDefault();
  const resultDiv = document.getElementById("schemeResult");
  resultDiv.textContent = "⏳ Finding best schemes for you...";
  const profile = {
    age: +document.getElementById("age").value,
    gender: document.getElementById("gender").value,
    occupation: document.getElementById("occupation").value,
    income: +document.getElementById("income").value,
    state: document.getElementById("state").value
  };
  try {
    const res = await fetch(`${API}/recommend-schemes`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(profile)
    });
    const data = await res.json();
    resultDiv.textContent = data.recommendations;
  } catch { resultDiv.textContent = "⚠️ Error."; }
};

// TRACK
async function trackComplaint() {
  const id = document.getElementById("trackId").value.trim();
  const div = document.getElementById("trackResult");
  if (!id) return;
  const res = await fetch(`${API}/complaint/${id}`);
  const data = await res.json();
  if (data.error) div.textContent = "❌ " + data.error;
  else div.innerHTML = `
    <div class="complaint-card">
      <h3>${data.id}</h3>
      <p><b>User:</b> ${data.user}</p>
      <p><b>Location:</b> ${data.location}</p>
      <p><b>Status:</b> <span class="status">${data.status}</span></p>
      <p><b>Filed:</b> ${new Date(data.filed_at).toLocaleString()}</p>
      <p><b>Description:</b> ${data.description}</p>
    </div>`;
}
async function loadAllComplaints() {
  const res = await fetch(`${API}/complaints`);
  const data = await res.json();
  const div = document.getElementById("allComplaints");
  if (!data.length) { div.textContent = "No complaints yet."; return; }
  div.innerHTML = data.map(c => `
    <div class="complaint-card">
      <b>${c.id}</b> · ${c.category} · <span class="status">${c.status}</span><br/>
      📍 ${c.location} — ${c.description.substring(0, 60)}...
    </div>`).join("");
}