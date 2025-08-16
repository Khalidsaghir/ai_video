async function generateVideo() {
  const prompt = document.getElementById("prompt").value.trim();
  if (!prompt) {
    alert("Please enter a prompt.");
    return;
  }

  document.getElementById("loading").style.display = "block";
  document.getElementById("outputVideo").style.display = "none";

  try {
    const res = await fetch("http://localhost:5000/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: prompt })
    });

    if (!res.ok) {
      throw new Error(`Server returned ${res.status}`);
    }

    const data = await res.json();
    if (data.video_url) {
      const video = document.getElementById("outputVideo");
      video.src = data.video_url;
      video.style.display = "block";
    } else {
      alert(data.error || "Unknown error");
    }
  } catch (err) {
    console.error("Frontend error:", err);
    alert("Error: " + err.message);
  }

  document.getElementById("loading").style.display = "none";
}
