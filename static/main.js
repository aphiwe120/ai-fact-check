// 👉 1. API Configuration
const API_BASE_URL = "http://127.0.0.1:5001";  

// 👉 2. Test API connection on page load
async function testAPI() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        return response.ok;
    } catch (error) {
        console.error("API connection test failed:", error);
        return false;
    }
}

// 👉 3. Main function to fetch fact-check results
async function fetchFactCheck(claim) {
    console.log("🔍 Sending claim to API:", claim);
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/check-claims?claim=${encodeURIComponent(claim)}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            },
        });
        
        console.log("📡 Response status:", response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        const data = await response.json();
        console.log("✅ API response received:", data);
        return data;
    } catch (error) {
        console.error('❌ Fetch error details:', error);
        throw new Error(`Failed to connect to API: ${error.message}`);
    }
}

// 👉 4. Fact Check Button Event Handler
document.getElementById("factCheckBtn").addEventListener("click", async () => {
    const claim = document.getElementById("claimInput").value.trim();
    
    // Validate input
    if (!claim) {
        alert("Please enter a claim to fact-check!");
        return;
    }

    if (claim.length < 5) {
        alert("Please enter a more detailed claim (at least 5 characters).");
        return;
    }

    console.log("🔄 Fact check button clicked, claim:", claim);

    // Test API connection first
    const apiAvailable = await testAPI();
    if (!apiAvailable) {
        alert("❌ Backend server is not running!\n\nPlease make sure:\n1. Flask server is running on port 5001\n2. Run: python app_sqlmodel.py\n3. Check terminal for errors");
        return;
    }

    // UI State Management
    document.getElementById("intro").classList.add("hidden");
    document.getElementById("loading").classList.remove("hidden");
    document.getElementById("result").classList.add("hidden");

    try {
        console.log("🔄 Fetching fact check...");
        const data = await fetchFactCheck(claim);
        console.log("📊 Received data:", data);

        // --- Populate UI with results ---
        
        // Claim Text
        document.getElementById("claimText").innerText = `"${data.claim}"`;
        
        // Verdict and Styling
        const verdictText = document.getElementById("verdictText");
        const verdictIcon = document.getElementById("verdictIcon");
        const resultHeader = document.getElementById("resultHeader");

        // Reset styles
        resultHeader.className = "result-header";

        // Enhanced verdict mapping
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
        } else if (data.verdict === "partially-true") {
            verdictText.innerText = "Partially True";
            verdictIcon.innerText = "➗";
            resultHeader.classList.add("partially-true");
        } else {
            verdictText.innerText = "Analysis Complete";
            verdictIcon.innerText = "ℹ️";
            resultHeader.classList.add("unclear");
        }

        // Credibility Score with color coding
        const credibilityScore = data.credibilityScore || 50;
        document.getElementById("credibilityScore").innerText = credibilityScore + "%";
        
        // Add color class to credibility score
        const scoreElement = document.getElementById("credibilityScore");
        scoreElement.className = ""; // Reset classes
        if (credibilityScore >= 80) {
            scoreElement.classList.add("high-credibility");
        } else if (credibilityScore >= 60) {
            scoreElement.classList.add("medium-credibility");
        } else {
            scoreElement.classList.add("low-credibility");
        }

        // Summary
        const summaryText = data.summary || "No summary available from the analysis.";
        document.getElementById("summaryText").innerText = summaryText;

        // Date
        const checkedDate = data.checkedAt || new Date().toISOString().split('T')[0];
        document.getElementById("checkedAt").innerText = formatDate(checkedDate);

        // Sources
        const sourcesList = document.getElementById("sourcesList");
        sourcesList.innerHTML = "";
        
        if (data.sources && data.sources.length > 0) {
            data.sources.forEach((src, index) => {
                const li = document.createElement("li");
                li.innerHTML = `
                    <a href="${src.url || '#'}" target="_blank" rel="noopener noreferrer">
                        ${src.title || `Source ${index + 1}`}
                    </a> 
                    <span class="tag credibility-${src.credibility || 'medium'}">${src.credibility || 'medium'}</span>
                `;
                sourcesList.appendChild(li);
            });
        } else {
            const li = document.createElement("li");
            li.innerHTML = `<span class="no-sources">No specific sources cited in this analysis.</span>`;
            sourcesList.appendChild(li);
        }

        // Related Claims
        const relatedList = document.getElementById("relatedList");
        relatedList.innerHTML = "";
        
        if (data.relatedClaims && data.relatedClaims.length > 0) {
            data.relatedClaims.forEach((rc, index) => {
                const li = document.createElement("li");
                li.textContent = rc;
                relatedList.appendChild(li);
            });
        } else {
            const li = document.createElement("li");
            li.innerHTML = `<span class="no-related">No related claims identified.</span>`;
            relatedList.appendChild(li);
        }

        // Show results, hide loader
        document.getElementById("loading").classList.add("hidden");
        document.getElementById("result").classList.remove("hidden");
        
        // Smooth scroll to results
        document.getElementById("result").scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });

    } catch (err) {
        console.error("❌ Full error details:", err);
        
        // Show user-friendly error message
        let errorMessage = "Could not fetch fact-check result. ";
        
        if (err.message.includes("Failed to fetch")) {
            errorMessage += "Please check if the backend server is running.";
        } else if (err.message.includes("500")) {
            errorMessage += "Server error occurred. Please try again later.";
        } else {
            errorMessage += `Error: ${err.message}`;
        }
        
        alert(errorMessage);
        
        // Reset UI state
        document.getElementById("loading").classList.add("hidden");
        document.getElementById("intro").classList.remove("hidden");
    }
});

// 👉 5. Reset for new check
function newCheck() {
    document.getElementById("result").classList.add("hidden");
    document.getElementById("intro").classList.remove("hidden");
    document.getElementById("claimInput").value = "";
    document.getElementById("claimInput").focus(); // Focus back to input
    
    // Smooth scroll back to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// 👉 6. Utility Functions
function formatDate(dateString) {
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
    } catch (e) {
        return dateString || "Unknown date";
    }
}

// 👉 7. Enter key support for claim input
document.getElementById("claimInput").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        document.getElementById("factCheckBtn").click();
    }
});

// 👉 8. Page load initialization
window.addEventListener('load', async () => {
    console.log("🚀 Checkmate Fact-Checker loaded");
    console.log("🔌 Testing API connection...");
    
    const apiAvailable = await testAPI();
    if (apiAvailable) {
        console.log("✅ API is connected and ready!");
        // Optional: Show a subtle connected indicator
        document.body.classList.add("api-connected");
    } else {
        console.warn("❌ API is not available");
        document.body.classList.add("api-disconnected");
    }
    
    // Add some helpful console messages
    console.log("💡 Tips:");
    console.log("- Enter a claim and click 'Fact Check' to verify information");
    console.log("- Press Enter in the input field to quickly submit");
    console.log("- Check the browser console for detailed debugging info");
});

// 👉 9. Enhanced error handling for network issues
window.addEventListener('online', () => {
    console.log("✅ Internet connection restored");
    document.body.classList.remove("offline");
});

window.addEventListener('offline', () => {
    console.warn("❌ Internet connection lost");
    document.body.classList.add("offline");
    alert("Internet connection lost. Please check your network.");
});