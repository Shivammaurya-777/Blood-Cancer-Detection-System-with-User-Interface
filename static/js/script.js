// Sign Up Logic
document.getElementById("signupForm")?.addEventListener("submit", async function(e) {
    e.preventDefault(); // Stop page from refreshing

    const formData = new FormData(this);

    try {
        const response = await fetch("/api/signup", {
            method: "POST",
            body: formData
        });

        if (response.ok) {
            alert("Registration Successful!");
            // Redirect to dashboard after successful signup
            window.location.href = "/dashboard";
        } else {
            const error = await response.json();
            alert("Error: " + error.detail);
        }
    } catch (error) {
        alert("Error: " + error.message);
    }
});

// verified login details
document.getElementById("loginForm")?.addEventListener("submit", async function(e) {
    e.preventDefault(); // Stop the page from just jumping to /dashboard

    const formData = new FormData(this);
    const userId = formData.get("user_id");

    try {
        // Call the login API
        const response = await fetch("/login", {
            method: "POST",
            body: formData
        });

        if (response.ok) {
            // Store user ID in localStorage for later use
            localStorage.setItem("userId", userId);
            // Only redirect if the database says the password is correct
            window.location.href = "/dashboard";
        } else {
            // Show the error message
            const error = await response.json();
            alert("Error: " + error.detail);
        }
    } catch (error) {
        alert("Error: " + error.message);
    }
});


// Search Patient
async function searchPatient() {
    let patientId = document.getElementById("patient_id").value;

    if (patientId === "") {
        alert("Enter Patient ID");
        return;
    }

    try {
        const response = await fetch(`/patient/${patientId}`);
        const data = await response.json();

        if (!data.error) {
            document.getElementById("detail_patient_id").innerText = patientId;
            document.getElementById("detail_patient_name").innerText = data.patient_name;
            document.getElementById("hidden_patient_id").value = patientId;
            document.querySelector("input[name='patient_name']").value = data.patient_name;
            document.getElementById("detail_class").innerText = data.detected_class || "-";
            document.getElementById("detail_confidence").innerText = data.confidence_score ? `${(data.confidence_score * 100).toFixed(2)}%` : "-";
            document.getElementById("detail_date").innerText = data.created_at || "-";
            document.getElementById("detail_symptoms").innerText = data.symptoms || "-";
        } else {
            alert("Patient not found");
        }
    } catch (error) {
        alert("Error searching patient: " + error.message);
    }
}


// Upload + Prediction
document.getElementById("uploadForm")?.addEventListener("submit", async function(e) 
{
    e.preventDefault();

    const formData = new FormData(this);

    // Generate patient_id if not set
    let patientId = document.getElementById("hidden_patient_id").value;
    if (!patientId) {
        patientId = "P" + Date.now();
        document.getElementById("hidden_patient_id").value = patientId;
        formData.set("patient_id", patientId);
    }

    // Set user_id from localStorage
    const userId = localStorage.getItem("userId");
    if (userId) {
        formData.set("user_id", userId);
    } else {
        alert("User not logged in. Please login first.");
        window.location.href = "/";
        return;
    }

    try {
        const response = await fetch("/predict", {
            method: "POST",
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            const now = new Date().toLocaleString();
            const patientName = document.querySelector("input[name='patient_name']").value || "-";

            document.getElementById("detail_patient_id").innerText = patientId;
            document.getElementById("detail_patient_name").innerText = patientName;
            document.getElementById("detail_class").innerText = data.predicted_class;
            document.getElementById("detail_confidence").innerText = `${(data.confidence * 100).toFixed(2)}%`;
            document.getElementById("detail_date").innerText = now;
            document.getElementById("detail_symptoms").innerText = data.symptoms || "-";
        } else {
            // Handle non-JSON error responses
            let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.message || errorMessage;
            } catch (jsonError) {
                // If response is not JSON, try to get text
                try {
                    const textResponse = await response.text();
                    // Extract meaningful error from HTML if possible
                    if (textResponse.includes('Internal Server Error')) {
                        errorMessage = "Server Error: Internal Server Error. Please check server logs.";
                    } else if (textResponse.includes('Bad Request')) {
                        errorMessage = "Bad Request: Please check your input data.";
                    } else {
                        errorMessage = `Server Error: ${textResponse.substring(0, 100)}...`;
                    }
                } catch (textError) {
                    errorMessage = `HTTP ${response.status}: ${response.statusText}`;
                }
            }
            console.log("Response not ok:", response.status, errorMessage);
            alert("Error uploading image: " + errorMessage);
        }
    } catch (error) {
        console.error("Upload error:", error);
        alert("Error uploading image: " + error.message);
    }
});


// Get History Function
async function getHistory() {
    let patientId = document.getElementById("history_patient_id").value;

    if (patientId === "") {
        alert("Enter Patient ID");
        return;
    }

    try {
        const response = await fetch(`/history/${patientId}`);
        const data = await response.json();

        let table = document.getElementById("history_table");

        if (data.history.length === 0) {
            table.innerHTML = `
                <tr>
                    <th>Image</th>
                    <th>Class</th>
                    <th>Confidence</th>
                    <th>Date</th>
                </tr>
                <tr>
                    <td colspan="4" style="text-align:center;">No history found</td>
                </tr>
            `;
            return;
        }

        // Clear old rows
        table.innerHTML = `
            <tr>
                <th>Image</th>
                <th>Class</th>
                <th>Confidence</th>
                <th>Date</th>
            </tr>
        `;

        data.history.forEach(item => {
            table.innerHTML += `
                <tr>
                    <td><img src="/${item.image}" width="80"></td>
                    <td>${item.class}</td>
                    <td>${(item.confidence * 100).toFixed(2)}%</td>
                    <td>${item.date}</td>
                </tr>
            `;
        });
    } catch (error) {
        alert("Error fetching history: " + error.message);
    }
}

// Feedback Form Logic
document.getElementById("feedbackForm")?.addEventListener("submit", async function(e) {
    e.preventDefault();

    // Get user ID from localStorage
    const userId = localStorage.getItem("userId");
    if (!userId) {
        alert("Please login first");
        window.location.href = "/";
        return;
    }

    // Set the userid in the form
    document.getElementById("userid").value = userId;

    const formData = new FormData(this);

    try {
        const response = await fetch("/feedback", {
            method: "POST",
            body: formData
        });

        if (response.ok) {
            alert("Feedback submitted successfully!");
            this.reset(); // Clear the form
        } else {
            const error = await response.json();
            alert("Error: " + error.detail);
        }
    } catch (error) {
        alert("Error: " + error.message);
    }
});

// Logout Handler
document.addEventListener("DOMContentLoaded", function() {
    const logoutLink = document.querySelector('a[href="/"]');
    if (logoutLink && logoutLink.textContent.toLowerCase().includes('logout')) {
        logoutLink.addEventListener("click", function(e) {
            localStorage.removeItem("userId");
        });
    }
});