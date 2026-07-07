// ---------- FORGOT PASSWORD (2-step: email -> security question -> reset) ----------
const emailForm = document.getElementById("email-form");
if (emailForm) {
  let currentEmail = "";

  emailForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideAlert("alert-box");
    currentEmail = document.getElementById("email").value;

    const submitBtn = e.target.querySelector("button[type=submit]");
    submitBtn.disabled = true;
    submitBtn.textContent = "Checking...";

    try {
      const data = await apiRequest("/admin/forgot-password/question", {
        method: "POST",
        auth: false,
        body: { email: currentEmail },
      });

      document.getElementById("question-display").textContent = data.question;
      emailForm.classList.add("hidden");
      document.getElementById("reset-form").classList.remove("hidden");
    } catch (err) {
      showAlert("alert-box", err.message);
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Continue";
    }
  });

  document.getElementById("reset-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    hideAlert("alert-box");

    const submitBtn = e.target.querySelector("button[type=submit]");
    submitBtn.disabled = true;
    submitBtn.textContent = "Resetting...";

    try {
      await apiRequest("/admin/forgot-password/reset", {
        method: "POST",
        auth: false,
        body: {
          email: currentEmail,
          answer: document.getElementById("answer").value,
          new_password: document.getElementById("new_password").value,
        },
      });

      const successBox = document.getElementById("success-box");
      successBox.textContent = "Password reset successful. Redirecting to login...";
      successBox.classList.remove("hidden");
      setTimeout(() => { window.location.href = "/admin"; }, 1800);
    } catch (err) {
      showAlert("alert-box", err.message);
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Reset Password";
    }
  });
}

// ---------- CHANGE PASSWORD (logged-in admin) ----------
const changePasswordForm = document.getElementById("change-password-form");
if (changePasswordForm) {
  Auth.requireRole("admin");

  changePasswordForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideAlert("alert-box");
    document.getElementById("success-box").classList.add("hidden");

    const submitBtn = e.target.querySelector("button[type=submit]");
    submitBtn.disabled = true;
    submitBtn.textContent = "Updating...";

    try {
      await apiRequest("/admin/change-password", {
        method: "POST",
        body: {
          current_password: document.getElementById("current_password").value,
          new_password: document.getElementById("new_password").value,
        },
      });

      const successBox = document.getElementById("success-box");
      successBox.textContent = "Password updated successfully.";
      successBox.classList.remove("hidden");
      changePasswordForm.reset();
    } catch (err) {
      showAlert("alert-box", err.message);
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Update Password";
    }
  });
}
