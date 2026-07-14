async function loadLandingStats() {
  try {
    const stats = await apiRequest("/stats", { auth: false });
    document.getElementById("stat-doctors").textContent = stats.doctors;
    document.getElementById("stat-patients").textContent = stats.patients;
    document.getElementById("stat-feedbacks").textContent = stats.feedbacks;
  } catch (err) {
    console.error("Failed to load stats", err);
  }
}

loadLandingStats();
setInterval(loadLandingStats, 30000);
