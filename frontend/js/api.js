// Shared API helper for all pages.
// Change this if your backend runs on a different host/port.
const API_BASE = "http://localhost:8000";

const Auth = {
  setToken(token, role) {
    localStorage.setItem("bcs_token", token);
    localStorage.setItem("bcs_role", role);
  },
  getToken() {
    return localStorage.getItem("bcs_token");
  },
  getRole() {
    return localStorage.getItem("bcs_role");
  },
  clear() {
    localStorage.removeItem("bcs_token");
    localStorage.removeItem("bcs_role");
  },
  requireRole(role) {
    const token = this.getToken();
    const currentRole = this.getRole();
    if (!token || currentRole !== role) {
      window.location.href = role === "admin" ? "/admin" : "/doctor/login";
    }
  },
};

async function apiRequest(path, { method = "GET", body = null, isForm = false, auth = true } = {}) {
  const headers = {};
  if (!isForm) headers["Content-Type"] = "application/json";
  if (auth) {
    const token = Auth.getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: isForm ? body : body ? JSON.stringify(body) : null,
  });

  let data = null;
  try {
    data = await response.json();
  } catch (e) {
    data = null;
  }

  if (!response.ok) {
    const message = (data && data.detail) || `Request failed (${response.status})`;
    throw new Error(message);
  }
  return data;
}

function showAlert(elementId, message, type = "error") {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.textContent = message;
  el.className = `alert alert-${type}`;
  el.classList.remove("hidden");
}

function hideAlert(elementId) {
  const el = document.getElementById(elementId);
  if (el) el.classList.add("hidden");
}

function imageUrl(path) {
  // Backend returns paths like "app/static/uploads/xyz.jpg" — map to served /static/...
  if (!path) return "";
  const idx = path.indexOf("static/");
  return idx >= 0 ? `${API_BASE}/${path.substring(idx)}` : path;
}
