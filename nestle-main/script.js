document.addEventListener("DOMContentLoaded", () => {
    fetch("http://127.0.0.1:5000/sentiment-data")
        .then(response => response.json())
        .then(data => {
            console.log(data); // Log the data to inspect its structure
            document.getElementById("sentiment-score").textContent = JSON.stringify(data.overallSentimentScore, null, 2); // Display the object as a formatted string
            document.getElementById("positive-score").textContent = `${data.positiveScore}%`;
            document.getElementById("neutral-score").textContent = `${data.neutralScore}%`;
            document.getElementById("negative-score").textContent = `${data.negativeScore}%`;
            renderSentimentTrendChart(data.trend);
        })
        .catch(error => console.error("Error fetching sentiment data:", error));
});

function renderSentimentTrendChart(trendData) {
    // Example chart rendering logic
    const positive = trendData.filter(item => item.sentiment === "positive").length;
    const neutral = trendData.filter(item => item.sentiment === "neutral").length;
    const negative = trendData.filter(item => item.sentiment === "negative").length;

    const ctx = document.getElementById('sentiment-chart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Positive', 'Neutral', 'Negative'],
            datasets: [{
                data: [positive, neutral, negative],
                backgroundColor: ['#28a745', '#ffc107', '#dc3545']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top'
                }
            }
        }
    });
}
