const input = document.getElementById("searchInput");
const suggestionsBox = document.getElementById("suggestions");

// =========================
// 1. LIVE AUTO SUGGESTIONS
// =========================
input.addEventListener("input", async () => {
    let query = input.value.trim();

    // Clear suggestions if empty
    if (query.length === 0) {
        suggestionsBox.innerHTML = "";
        return;
    }

    try {
        let response = await fetch(`/suggest?q=${query}`);
        let data = await response.json();

        suggestionsBox.innerHTML = "";

        data.forEach(item => {
            let li = document.createElement("li");
            li.innerText = item;

            // click suggestion → auto fill + search
            li.onclick = () => {
                input.value = item;
                suggestionsBox.innerHTML = "";
                search();
            };

            suggestionsBox.appendChild(li);
        });

    } catch (error) {
        console.log("Suggestion error:", error);
    }
});


// =========================
// 2. SEARCH FUNCTION
// =========================
async function search() {
    let query = input.value.trim();

    if (query.length === 0) return;

    try {
        let response = await fetch("/search", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ query: query })
        });

        let data = await response.json();

        // Show answer
        document.getElementById("answer").innerText = data.answer;

        // Show spelling suggestion (if any)
        document.getElementById("suggestion").innerText =
            data.suggestion ? data.suggestion : "";

        // Clear suggestions after search
        suggestionsBox.innerHTML = "";

    } catch (error) {
        console.log("Search error:", error);
    }
}


// =========================
// 3. ENTER KEY SUPPORT
// =========================
input.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        search();
    }
});