async function handleLogin() {
  const username = document.getElementById("username").value.trim();
  const errEl = document.getElementById("login-err");
  const btn = document.getElementById("login-btn");

  errEl.textContent = "";

  if (!username) {
    errEl.textContent = "Please enter a captain name.";
    return;
  }

  btn.disabled = true;
  btn.textContent = "Setting sail...";

  try {
    const formData = new FormData();
    formData.append("username", username);

    const response = await fetch("/", {
      method: "POST",
      body: formData,
    });

    if (response.redirected) {
      window.location.href = response.url;
    } else if (!response.ok) {
      const data = await response.json();
      errEl.textContent = data.error || "Login failed. Please try again.";
    }
  } catch (err) {
    errEl.textContent = "Network error. Please try again.";
  } finally {
    btn.disabled = false;
    btn.textContent = "🌊 Login to Fleet Command";
  }
}