Auth.requireRole("doctor");

// ---------- Sidebar section switching ----------
document.querySelectorAll(".nav-link").forEach((link) => {
  link.addEventListener("click", (e) => {
    e.preventDefault();
    document.querySelectorAll(".nav-link").forEach((l) => l.classList.remove("active"));
    link.classList.add("active");

    document.querySelectorAll(".section").forEach((s) => s.classList.add("hidden"));
    document.getElementById(`section-${link.dataset.section}`).classList.remove("hidden");
  });
});

document.getElementById("logout-btn").addEventListener("click", () => {
  Auth.clear();
  window.location.href = "/doctor/login";
});

// ---------- Prediction ----------
document.getElementById("predict-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  hideAlert("predict-alert");
  document.getElementById("result-card").classList.add("hidden");

  const formData = new FormData();
  formData.append("patient_name", document.getElementById("patient_name").value);
  formData.append("cell_image", document.getElementById("cell_image").files[0]);

  const submitBtn = e.target.querySelector("button[type=submit]");
  submitBtn.disabled = true;
  submitBtn.textContent = "Analyzing...";

  try {
    const result = await apiRequest("/predict", { method: "POST", body: formData, isForm: true });

    document.getElementById("result-image").src = imageUrl(result.cell_image_path);
    document.getElementById("result-patient-name").textContent = result.patient_name;
    document.getElementById("result-patient-id").textContent = result.patient_id;
    document.getElementById("result-cancer-type").textContent = result.cancer_type;
    document.getElementById("result-confidence").textContent = `${result.confidence}%`;
    document.getElementById("result-confidence-bar").style.width = `${result.confidence}%`;
    document.getElementById("result-symptoms").textContent = result.symptoms;
    document.getElementById("result-medicines").textContent = result.medicines;

    document.getElementById("result-card").classList.remove("hidden");
    document.getElementById("predict-form").reset();
  } catch (err) {
    showAlert("predict-alert", err.message);
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Submit for prediction";
  }
});

// ---------- Patient history ----------
document.getElementById("history-search-btn").addEventListener("click", async () => {
  hideAlert("history-alert");
  document.getElementById("history-result-card").classList.add("hidden");

  const patientId = document.getElementById("history-search-id").value.trim();
  if (!patientId) {
    showAlert("history-alert", "Enter a patient ID to search.");
    return;
  }

  try {
    const patient = await apiRequest(`/patients/${encodeURIComponent(patientId)}`);

    document.getElementById("history-patient-title").textContent = `${patient.patient_name} — ${patient.patient_id}`;
    document.getElementById("history-patient-created").textContent = `First recorded: ${new Date(patient.created_at).toLocaleString()}`;

    const tbody = document.getElementById("history-table-body");
    tbody.innerHTML = "";
    patient.predictions.forEach((p) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${new Date(p.created_at).toLocaleString()}</td>
        <td>${p.cancer_type}</td>
        <td>${p.confidence}%</td>
        <td>${p.symptoms}</td>
        <td>${p.medicines}</td>
      `;
      tbody.appendChild(row);
    });

    document.getElementById("history-result-card").classList.remove("hidden");
  } catch (err) {
    showAlert("history-alert", err.message);
  }
});

// ---------- Feedback ----------
document.getElementById("feedback-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  hideAlert("feedback-alert");
  document.getElementById("feedback-success").classList.add("hidden");

  const ratings = {
    ease_of_use: document.getElementById("q_ease").value,
    accuracy: document.getElementById("q_accuracy").value,
    would_recommend: document.getElementById("q_recommend").value,
  };

  const submitBtn = e.target.querySelector("button[type=submit]");
  submitBtn.disabled = true;
  submitBtn.textContent = "Submitting...";

  try {
    await apiRequest("/feedback", {
      method: "POST",
      body: {
        ratings_json: JSON.stringify(ratings),
        comments: document.getElementById("comments").value,
      },
    });
    document.getElementById("feedback-form").reset();
    const successBox = document.getElementById("feedback-success");
    successBox.textContent = "Thank you — your feedback has been submitted.";
    successBox.classList.remove("hidden");
  } catch (err) {
    showAlert("feedback-alert", err.message);
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Submit feedback";
  }
});
// ---------- Stat boxes ----------
async function loadDashboardStats() {
  try {
    const stats = await apiRequest("/stats", { auth: false });
    document.getElementById("stat-doctors").textContent = stats.doctors;
    document.getElementById("stat-patients").textContent = stats.patients;
    document.getElementById("stat-feedbacks").textContent = stats.feedbacks;
  } catch (err) {
    console.error("Failed to load stats", err);
  }
}
loadDashboardStats();
setInterval(loadDashboardStats, 30000);