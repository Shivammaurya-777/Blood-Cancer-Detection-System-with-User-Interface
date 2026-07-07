document.getElementById("register-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  hideAlert("alert-box");
  document.getElementById("success-box").classList.add("hidden");

  const formData = new FormData();
  formData.append("full_name", document.getElementById("full_name").value);
  formData.append("mobile_number", document.getElementById("mobile_number").value);
  formData.append("gender", document.getElementById("gender").value);
  formData.append("email", document.getElementById("email").value);
  formData.append("degree", document.getElementById("degree").value);
  formData.append("degree_image", document.getElementById("degree_image").files[0]);

  const submitBtn = e.target.querySelector("button[type=submit]");
  submitBtn.disabled = true;
  submitBtn.textContent = "Submitting...";

  try {
    await apiRequest("/register", { method: "POST", body: formData, isForm: true, auth: false });
    document.getElementById("register-form").reset();
    const successBox = document.getElementById("success-box");
    successBox.textContent = "Registration request submitted. You'll be notified by email and SMS once an admin reviews it.";
    successBox.classList.remove("hidden");
  } catch (err) {
    showAlert("alert-box", err.message);
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Submit registration request";
  }
});
