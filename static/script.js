document.getElementById("demoForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const input = document.getElementById("profileUrl");
  const output = document.getElementById("output");
  const submitButton = e.submitter;

  const profileUrl = input.value.trim();
  if (!profileUrl) {
    output.textContent = "Please enter a profile URL.";
    return;
  }

  output.textContent = "Generating Persona..";
  if (submitButton) {
    submitButton.disabled = true;
    submitButton.textContent = "Processing...";
  }

  try {
    const response = await fetch("/generate_persona", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ profileUrl })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    output.innerText = data.persona || "Persona generated!";
  } 
  catch (error) {
    console.error("Fetch error:", error);
    output.textContent = "Error: " + error.message;
  } finally {
    if (submitButton) {
      submitButton.disabled = false;
      submitButton.textContent = "Submit";
    }
  }


});
