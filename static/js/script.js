async function checkText() {
    const text = document.getElementById("inputText").value;
    const response = await fetch("/correct-text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text })
    });
    const data = await response.json();

    document.getElementById("correctedText").innerText = data.corrected_text;
    document.getElementById("highlightedMistakes").innerHTML = data.highlighted_mistakes;

    let insightsList = document.getElementById("learningInsights");
    insightsList.innerHTML = "";
    document.getElementById("noMistakes").style.display = "none";

    // Only show learning insights if they exist
    if (data.learning_insights.length > 0) {
        data.learning_insights.forEach(insight => {
            let li = document.createElement("li");
            li.innerText = insight;
            insightsList.appendChild(li);
        });
    } else {
        document.getElementById("noMistakes").style.display = "block";
    }
}
