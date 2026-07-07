Auth.requireRole("admin");

let currentRequestId = null;

// ---------- Sidebar section switching ----------
document.querySelectorAll(".nav-link").forEach((link) => {
  link.addEventListener("click", (e) => {
    e.preventDefault();
    document.querySelectorAll(".nav-link").forEach((l) => l.classList.remove("active"));
    link.classList.add("active");

    document.querySelectorAll(".section").forEach((s) => s.classList.add("hidden"));
    document.getElementById(`section-${link.dataset.section}`).classList.remove("hidden");

    if (link.dataset.section === "requests") loadRequests();
    if (link.dataset.section === "doctors") loadDoctors();
    if (link.dataset.section === "feedback") loadFeedback();
  });
});

document.getElementById("logout-btn").addEventListener("click", () => {
  Auth.clear();
  window.location.href = "/admin";
});

// ---------- Stat boxes ----------
async function loadDashboardStats() {
  try {
    const stats = await apiRequest("/stats", { auth: false });
    document.getElementById("stat-doctors").textContent = stats.doctors;
    document.getElementById("stat-predictions").textContent = stats.predictions;
    document.getElementById("stat-patients").textContent = stats.patients;
    document.getElementById("stat-feedbacks").textContent = stats.feedbacks;
  } catch (err) {
    console.error("Failed to load stats", err);
  }
}
loadDashboardStats();
setInterval(loadDashboardStats, 30000);

function statusBadge(status) {
  return `<span class="badge badge-${status}">${status}</span>`;
}

// ---------- Requests list ----------
async function loadRequests() {
  hideAlert("requests-alert");
  document.getElementById("request-detail-card").classList.add("hidden");
  document.getElementById("requests-list-card").classList.remove("hidden");

  try {
    const requests = await apiRequest("/admin/requests?status_filter=all");
    const tbody = document.getElementById("requests-table-body");
    tbody.innerHTML = "";

    document.getElementById("requests-empty").classList.toggle("hidden", requests.length > 0);

    requests.forEach((r) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${r.full_name}</td>
        <td>${r.email}</td>
        <td>${r.degree}</td>
        <td>${new Date(r.created_at).toLocaleDateString()}</td>
        <td>${statusBadge(r.status)}</td>
        <td><button class="btn btn-outline view-detail-btn" data-id="${r.id}">View details</button></td>
      `;
      tbody.appendChild(row);
    });

    document.querySelectorAll(".view-detail-btn").forEach((btn) => {
      btn.addEventListener("click", () => showRequestDetail(btn.dataset.id));
    });
  } catch (err) {
    showAlert("requests-alert", err.message);
  }
}

async function showRequestDetail(requestId) {
  hideAlert("requests-alert");
  currentRequestId = requestId;

  try {
    const r = await apiRequest(`/admin/requests/${requestId}`);

    document.getElementById("detail-name").textContent = r.full_name;
    document.getElementById("detail-image").src = imageUrl(r.degree_image_path);
    document.getElementById("detail-mobile").textContent = r.mobile_number;
    document.getElementById("detail-gender").textContent = r.gender;
    document.getElementById("detail-email").textContent = r.email;
    document.getElementById("detail-degree").textContent = r.degree;
    document.getElementById("detail-status").innerHTML = statusBadge(r.status);

    document.getElementById("approve-panel").classList.add("hidden");
    document.getElementById("reject-panel").classList.add("hidden");
    document.getElementById("detail-actions").classList.toggle("hidden", r.status !== "pending");

    document.getElementById("requests-list-card").classList.add("hidden");
    document.getElementById("request-detail-card").classList.remove("hidden");
  } catch (err) {
    showAlert("requests-alert", err.message);
  }
}

document.getElementById("back-to-list-btn").addEventListener("click", loadRequests);

document.getElementById("show-approve-btn").addEventListener("click", () => {
  document.getElementById("reject-panel").classList.add("hidden");
  document.getElementById("approve-panel").classList.remove("hidden");
});

document.getElementById("show-reject-btn").addEventListener("click", () => {
  document.getElementById("approve-panel").classList.add("hidden");
  document.getElementById("reject-panel").classList.remove("hidden");
});

document.getElementById("submit-approve-btn").addEventListener("click", async () => {
  const loginId = document.getElementById("approve-login-id").value.trim();
  const password = document.getElementById("approve-password").value.trim();
  if (!loginId || !password) {
    showAlert("requests-alert", "Enter both a login ID and password.");
    return;
  }
  try {
    await apiRequest(`/admin/requests/${currentRequestId}/approve`, {
      method: "POST",
      body: { login_id: loginId, password: password },
    });
    loadRequests();
  } catch (err) {
    showAlert("requests-alert", err.message);
  }
});

document.getElementById("submit-reject-btn").addEventListener("click", async () => {
  const reason = document.getElementById("reject-reason").value.trim();
  if (!reason) {
    showAlert("requests-alert", "Enter a reason for rejection.");
    return;
  }
  try {
    await apiRequest(`/admin/requests/${currentRequestId}/reject`, {
      method: "POST",
      body: { reason: reason },
    });
    loadRequests();
  } catch (err) {
    showAlert("requests-alert", err.message);
  }
});

// ---------- Doctor management ----------
async function loadDoctors() {
  hideAlert("doctors-alert");
  document.getElementById("doctor-edit-card").classList.add("hidden");
  document.getElementById("doctors-list-card").classList.remove("hidden");

  try {
    const doctors = await apiRequest("/admin/doctors");
    const tbody = document.getElementById("doctors-table-body");
    tbody.innerHTML = "";
    document.getElementById("doctors-empty").classList.toggle("hidden", doctors.length > 0);

    doctors.forEach((d) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${d.full_name}</td>
        <td>${d.login_id}</td>
        <td>${d.mobile_number}</td>
        <td>${d.email}</td>
        <td style="display:flex; gap:8px;">
          <button class="btn btn-outline edit-doctor-btn" data-id="${d.id}"
            data-full_name="${d.full_name}" data-email="${d.email}"
            data-mobile_number="${d.mobile_number}" data-gender="${d.gender}"
            data-login_id="${d.login_id}">Edit</button>
          <button class="btn btn-danger delete-doctor-btn" data-id="${d.id}" data-name="${d.full_name}">Delete</button>
        </td>
      `;
      tbody.appendChild(row);
    });

    document.querySelectorAll(".delete-doctor-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        if (!confirm(`Delete doctor "${btn.dataset.name}"? This revokes their login access.`)) return;
        try {
          await apiRequest(`/admin/doctors/${btn.dataset.id}`, { method: "DELETE" });
          loadDoctors();
        } catch (err) {
          showAlert("doctors-alert", err.message);
        }
      });
    });

    document.querySelectorAll(".edit-doctor-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.getElementById("edit-doctor-id").value = btn.dataset.id;
        document.getElementById("edit-full-name").value = btn.dataset.full_name;
        document.getElementById("edit-email").value = btn.dataset.email;
        document.getElementById("edit-mobile").value = btn.dataset.mobile_number;
        document.getElementById("edit-gender").value = btn.dataset.gender;
        document.getElementById("edit-login-id").value = btn.dataset.login_id;
        document.getElementById("edit-password").value = "";

        document.getElementById("doctors-list-card").classList.add("hidden");
        document.getElementById("doctor-edit-card").classList.remove("hidden");
      });
    });
  } catch (err) {
    showAlert("doctors-alert", err.message);
  }
}

document.getElementById("back-to-doctors-btn").addEventListener("click", loadDoctors);

document.getElementById("save-doctor-btn").addEventListener("click", async () => {
  hideAlert("doctors-alert");
  const doctorId = document.getElementById("edit-doctor-id").value;

  const payload = {
    full_name: document.getElementById("edit-full-name").value.trim(),
    email: document.getElementById("edit-email").value.trim(),
    mobile_number: document.getElementById("edit-mobile").value.trim(),
    gender: document.getElementById("edit-gender").value,
    login_id: document.getElementById("edit-login-id").value.trim(),
  };

  const newPassword = document.getElementById("edit-password").value.trim();
  if (newPassword) payload.new_password = newPassword;

  try {
    await apiRequest(`/admin/doctors/${doctorId}`, { method: "PUT", body: payload });
    loadDoctors();
  } catch (err) {
    showAlert("doctors-alert", err.message);
  }
});

// ---------- Feedback list ----------
async function loadFeedback() {
  hideAlert("feedback-list-alert");
  try {
    const feedbackItems = await apiRequest("/admin/feedback");
    const tbody = document.getElementById("feedback-table-body");
    tbody.innerHTML = "";
    document.getElementById("feedback-empty").classList.toggle("hidden", feedbackItems.length > 0);

    feedbackItems.forEach((f) => {
      let ratingsDisplay = f.ratings_json;
      try {
        const parsed = JSON.parse(f.ratings_json);
        ratingsDisplay = Object.entries(parsed).map(([k, v]) => `${k}: ${v}`).join(", ");
      } catch (e) { /* leave raw */ }

      const row = document.createElement("tr");
      row.innerHTML = `
        <td>#${f.doctor_id}</td>
        <td>${ratingsDisplay}</td>
        <td>${f.comments || "—"}</td>
        <td>${new Date(f.created_at).toLocaleString()}</td>
      `;
      tbody.appendChild(row);
    });
  } catch (err) {
    showAlert("feedback-list-alert", err.message);
  }
}

// Initial load
loadRequests();