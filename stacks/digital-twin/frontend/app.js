const state = { token: sessionStorage.getItem("digitalTwinToken") };

const loginPanel = document.querySelector("#login-panel");
const application = document.querySelector("#application");
const logoutButton = document.querySelector("#logout");

async function request(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (state.token) headers.set("Authorization", `Bearer ${state.token}`);
  if (options.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  const response = await fetch(path, { ...options, headers });
  if (response.status === 401) {
    signOut();
    throw new Error("Your session expired. Sign in again.");
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${response.status})`);
  }
  return response.status === 204 ? null : response.json();
}

function signOut() {
  state.token = null;
  sessionStorage.removeItem("digitalTwinToken");
  loginPanel.classList.remove("hidden");
  application.classList.add("hidden");
  logoutButton.classList.add("hidden");
}

async function loadApplication() {
  const [summary, devices, rooms, types] = await Promise.all([
    request("/api/v1/summary"),
    request("/api/v1/devices"),
    request("/api/v1/rooms"),
    request("/api/v1/lookups/device-types"),
  ]);

  document.querySelector("#summary").innerHTML = [
    ["Devices", summary.devices],
    ["Active", summary.active_devices],
    ["Rooms", summary.rooms],
    ["Components", summary.components],
    ["Purchases", summary.purchases],
  ].map(([label, value]) => `<article class="card"><strong>${value}</strong><span>${label}</span></article>`).join("");

  document.querySelector("#devices").innerHTML = devices.length
    ? devices.map((device) => `<tr><td>${escapeHtml(device.name)}</td><td>${escapeHtml(device.device_type.name)}</td><td>${escapeHtml(device.room?.name || "—")}</td><td>${escapeHtml(device.status)}</td></tr>`).join("")
    : '<tr><td colspan="4" class="empty">No devices yet.</td></tr>';

  document.querySelector("#rooms").innerHTML = '<option value="">Unassigned</option>' + rooms.map((room) => `<option value="${room.id}">${escapeHtml(room.name)}</option>`).join("");
  document.querySelector("#device-types").innerHTML = types.map((type) => `<option value="${type.id}">${escapeHtml(type.name)}</option>`).join("");
}

function escapeHtml(value) {
  const element = document.createElement("span");
  element.textContent = String(value);
  return element.innerHTML;
}

document.querySelector("#login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const error = document.querySelector("#login-error");
  error.textContent = "";
  const data = new URLSearchParams(new FormData(event.currentTarget));
  try {
    const response = await fetch("/api/v1/auth/token", { method: "POST", body: data });
    if (!response.ok) throw new Error("Incorrect username or password.");
    const token = await response.json();
    state.token = token.access_token;
    sessionStorage.setItem("digitalTwinToken", state.token);
    loginPanel.classList.add("hidden");
    application.classList.remove("hidden");
    logoutButton.classList.remove("hidden");
    await loadApplication();
  } catch (failure) {
    signOut();
    error.textContent = failure.message;
  }
});

document.querySelector("#device-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = document.querySelector("#device-message");
  const form = new FormData(event.currentTarget);
  const payload = Object.fromEntries(form.entries());
  payload.device_type_id = Number(payload.device_type_id);
  payload.room_id = payload.room_id ? Number(payload.room_id) : null;
  try {
    await request("/api/v1/devices", { method: "POST", body: JSON.stringify(payload) });
    message.textContent = "Device added.";
    event.currentTarget.reset();
    await loadApplication();
  } catch (failure) {
    message.textContent = failure.message;
  }
});

document.querySelector("#refresh").addEventListener("click", () => loadApplication().catch((failure) => window.alert(failure.message)));
logoutButton.addEventListener("click", signOut);

if (state.token) {
  loginPanel.classList.add("hidden");
  application.classList.remove("hidden");
  logoutButton.classList.remove("hidden");
  loadApplication().catch(() => signOut());
}
