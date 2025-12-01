// DOC Validator - Main JavaScript

let selectedFile = null;

// File input handling
document.getElementById("fileInput").addEventListener("change", function (e) {
  if (e.target.files.length > 0) {
    selectedFile = e.target.files[0];
    displayFileInfo(selectedFile);
    document.getElementById("analyzeBtn").disabled = false;
  }
});

// Drag and drop
const dropZone = document.getElementById("dropZone");

dropZone.addEventListener("dragover", function (e) {
  e.preventDefault();
  dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", function (e) {
  e.preventDefault();
  dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", function (e) {
  e.preventDefault();
  dropZone.classList.remove("dragover");

  if (e.dataTransfer.files.length > 0) {
    selectedFile = e.dataTransfer.files[0];
    if (selectedFile.name.endsWith(".csv")) {
      displayFileInfo(selectedFile);
      document.getElementById("analyzeBtn").disabled = false;
    } else {
      alert("Please upload a CSV file");
    }
  }
});

function displayFileInfo(file) {
  document.getElementById("fileName").textContent = file.name;
  document.getElementById("fileInfo").style.display = "flex";
}

function clearFile() {
  selectedFile = null;
  document.getElementById("fileInput").value = "";
  document.getElementById("fileInfo").style.display = "none";
  document.getElementById("analyzeBtn").disabled = true;
  document.getElementById("results").style.display = "none";
}

async function analyzeData() {
  if (!selectedFile) return;

  const formData = new FormData();
  formData.append("file", selectedFile);

  document.getElementById("loading").style.display = "flex";
  document.getElementById("results").style.display = "none";

  try {
    const response = await fetch("/api/validate", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    document.getElementById("loading").style.display = "none";

    if (data.error) {
      alert("Error: " + data.error);
      return;
    }

    if (data.success) {
      displayResults(data);
    }
  } catch (error) {
    document.getElementById("loading").style.display = "none";
    alert("Error processing file: " + error.message);
    console.error("Error:", error);
  }
}

function displayResults(data) {
  const resultsDiv = document.getElementById("results");
  let html = "<h2>Analysis Results</h2>";

  // Summary statistics
  html += '<div class="summary-stats">';
  html += `<div class="stat-card">
        <div class="stat-value">${data.summary.total_patients}</div>
        <div class="stat-label">Total Patients</div>
    </div>`;
  html += `<div class="stat-card">
        <div class="stat-value">${data.summary.avg_risk.toFixed(1)}%</div>
        <div class="stat-label">Average Risk</div>
    </div>`;
  html += `<div class="stat-card">
        <div class="stat-value">${data.summary.high_risk_count}</div>
        <div class="stat-label">High Risk Patients</div>
    </div>`;
  html += `<div class="stat-card">
        <div class="stat-value">${data.summary.high_risk_pct.toFixed(1)}%</div>
        <div class="stat-label">High Risk %</div>
    </div>`;
  html += "</div>";

  // Risk distribution plot
  if (data.plots.risk_distribution) {
    html += '<div class="plot-container">';
    html += "<h3>Risk Distribution</h3>";
    html += `<img src="${data.plots.risk_distribution}" alt="Risk Distribution">`;
    html += "</div>";
  }

  // Validation metrics (if outcomes provided)
  if (data.validation_metrics) {
    html += '<div class="validation-metrics">';
    html += "<h3>Validation Metrics</h3>";
    html += `<div class="metric-row">
            <span class="metric-label">AUC (Discrimination):</span>
            <span class="metric-value">${data.validation_metrics.auc.toFixed(
              3
            )}</span>
        </div>`;
    html += `<div class="metric-row">
            <span class="metric-label">Brier Score (Calibration):</span>
            <span class="metric-value">${data.validation_metrics.brier_score.toFixed(
              4
            )}</span>
        </div>`;
    html += `<div class="metric-row">
            <span class="metric-label">Event Rate:</span>
            <span class="metric-value">${data.validation_metrics.event_rate.toFixed(
              1
            )}%</span>
        </div>`;
    html += `<div class="metric-row">
            <span class="metric-label">Number of Events:</span>
            <span class="metric-value">${data.validation_metrics.n_events}</span>
        </div>`;
    html += "</div>";

    // ROC Curve
    if (data.plots.roc_curve) {
      html += '<div class="plot-container">';
      html += "<h3>ROC Curve</h3>";
      html += `<img src="${data.plots.roc_curve}" alt="ROC Curve">`;
      html += "</div>";
    }

    // Calibration Plot
    if (data.plots.calibration) {
      html += '<div class="plot-container">';
      html += "<h3>Calibration Plot</h3>";
      html += `<img src="${data.plots.calibration}" alt="Calibration Plot">`;
      html += "</div>";
    }

    // Risk Stratification
    if (data.validation_metrics.risk_stratification) {
      html += '<div class="validation-metrics">';
      html += "<h3>Risk Stratification</h3>";
      html += '<table style="width: 100%; border-collapse: collapse;">';
      html +=
        '<tr style="background: #f8f9fa;"><th style="padding: 10px; text-align: left;">Risk Category</th><th style="padding: 10px; text-align: right;">N Patients</th><th style="padding: 10px; text-align: right;">N Events</th><th style="padding: 10px; text-align: right;">Event Rate</th></tr>';

      const riskStrat = data.validation_metrics.risk_stratification;
      const categories = ["Low", "Moderate", "High", "Very High"];

      categories.forEach((cat) => {
        if (riskStrat[cat]) {
          html += `<tr>
                        <td style="padding: 10px;">${cat}</td>
                        <td style="padding: 10px; text-align: right;">${riskStrat[cat].n_patients}</td>
                        <td style="padding: 10px; text-align: right;">${riskStrat[cat].n_events}</td>
                        <td style="padding: 10px; text-align: right;">${riskStrat[cat].event_rate_pct}%</td>
                    </tr>`;
        }
      });

      html += "</table>";
      html += "</div>";
    }
  }

  // Download section
  html += '<div class="download-section">';
  html += "<h3>Download Predictions</h3>";
  html += "<p>Download the predictions as a CSV file</p>";
  html +=
    '<button class="download-btn" onclick="downloadPredictions()">Download CSV</button>';
  html += "</div>";

  resultsDiv.innerHTML = html;
  resultsDiv.style.display = "block";

  // Store predictions CSV for download
  window.predictionsCSV = data.predictions_csv;
}

function downloadPredictions() {
  if (!window.predictionsCSV) return;

  const blob = new Blob([window.predictionsCSV], { type: "text/csv" });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "DOC_predictions.csv";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}
