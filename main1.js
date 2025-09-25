// 👉 1. Replace this with your API base URL
const API_BASE_URL = "http://127.0.0.1:8000";  

// 👉 2. Adjust this function to call your API route
async function fetchFactCheck(claim) {
  // Example: if your API endpoint is /fact-check?claim=...
  const response = await fetch(`${API_BASE_URL}/fact-check?claim=${encodeURIComponent(claim)}`);
  
  if (!response.ok) {
    throw new Error("API request failed");
  }

  // 👉 3. Make sure your API returns JSON in this format:
  // {
  //   claim: "...",
  //   verdict: "true" | "false" | "unclear" | "partially-true",
  //   credibilityScore: 75,
  //   summary: "...",
  //   sources: [ { title: "...", url: "...", credibility: "high" } ],
  //   checkedAt: "2025-09-25",
  //   relatedClaims: ["..."]
  // }
  return await response.json();
}

// --- Fact Check Button ---
document.getElementById("factCheckBtn").addEventListener("click", async () => {
  const claim = document.getElementById("claimInput").value.trim();
  if (!claim) return alert("Please enter a claim!");

  // Hide intro, show loading spinner
  document.getElementById("intro").classList.add("hidden");
  document.getElementById("loading").classList.remove("hidden");

  try {
    // 👉 4. API call
    const data = await fetchFactCheck(claim);

    // --- Populate UI with results ---
    document.getElementById("claimText").innerText = `"${data.claim}"`;
    const verdictText = document.getElementById("verdictText");
    const verdictIcon = document.getElementById("verdictIcon");
    const resultHeader = document.getElementById("resultHeader");

    resultHeader.className = "result-header"; // reset styles

    if (data.verdict === "false") {
      verdictText.innerText = "Marked as False";
      verdictIcon.innerText = "❌";
      resultHeader.classList.add("false");
    } else if (data.verdict === "true") {
      verdictText.innerText = "Legitimate Claim";
      verdictIcon.innerText = "✅";
      resultHeader.classList.add("true");
    } else if (data.verdict === "unclear") {
      verdictText.innerText = "Unclear Information";
      verdictIcon.innerText = "⚠️";
      resultHeader.classList.add("unclear");
    } else {
      verdictText.innerText = "Partially True";
      verdictIcon.innerText = "➗";
      resultHeader.classList.add("unclear");
    }

    // --- Credibility ---
    document.getElementById("credibilityScore").innerText = data.credibilityScore + "%";

    // --- Summary ---
    document.getElementById("summaryText").innerText = data.summary;

    // --- Date ---
    document.getElementById("checkedAt").innerText = data.checkedAt || "Unknown";

    // --- Sources ---
    const sourcesList = document.getElementById("sourcesList");
    sourcesList.innerHTML = "";
    (data.sources || []).forEach((src) => {
      const li = document.createElement("li");
      li.innerHTML = `<a href="${src.url}" target="_blank">${src.title}</a> <span class="tag">${src.credibility}</span>`;
      sourcesList.appendChild(li);
    });

    // --- Related Claims ---
    const relatedList = document.getElementById("relatedList");
    relatedList.innerHTML = "";
    (data.relatedClaims || []).forEach((rc) => {
      const li = document.createElement("li");
      li.textContent = rc;
      relatedList.appendChild(li);
    });

    // Show results, hide loader
    document.getElementById("loading").classList.add("hidden");
    document.getElementById("result").classList.remove("hidden");

  } catch (err) {
    console.error("Error fetching fact-check:", err);
    alert("Could not fetch fact-check result. Please check your API.");
    document.getElementById("loading").classList.add("hidden");
    document.getElementById("intro").classList.remove("hidden");
  }
});

// --- Reset for new check ---
function newCheck() {
  document.getElementById("result").classList.add("hidden");
  document.getElementById("intro").classList.remove("hidden");
  document.getElementById("claimInput").value = "";
}
