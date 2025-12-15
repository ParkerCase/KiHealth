// DOC Validator - Main JavaScript

// API Configuration - Use Railway backend URL
// In production (Vercel), this will be the Railway API URL
// In development, use relative URLs for local testing
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? '' // Use relative URLs for local development
  : 'https://doc-production-5888.up.railway.app'; // Railway API URL for production

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

    // Read response body once (can only be read once)
    let responseText;
    try {
      responseText = await response.text();
    } catch (e) {
      document.getElementById("loading").style.display = "none";
      alert("Error: Failed to read server response. Please try again.");
      console.error("Response read error:", e);
      return;
    }

    // Check if response is OK
    if (!response.ok) {
      // Try to parse as JSON, fallback to text
      let errorMessage = `Server error (${response.status})`;
      try {
        const errorData = JSON.parse(responseText);
        errorMessage = errorData.error || errorMessage;
      } catch (e) {
        errorMessage = responseText || errorMessage;
      }
      document.getElementById("loading").style.display = "none";
      alert("Error: " + errorMessage);
      console.error("Server error:", response.status, errorMessage);
      return;
    }

    // Parse JSON response
    let data;
    try {
      data = JSON.parse(responseText);
    } catch (e) {
      document.getElementById("loading").style.display = "none";
      alert("Error: Invalid response from server. Please try again.");
      console.error(
        "JSON parse error:",
        e,
        "Response text:",
        responseText.substring(0, 200)
      );
      return;
    }

    document.getElementById("loading").style.display = "none";

    if (data.error) {
      alert("Error: " + data.error);
      return;
    }

    if (data.success) {
      displayResults(data);
    } else {
      alert("Error: Unexpected response format");
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

  // Check for missing data and display warnings
  const hasMissingPainScores = data.summary?.patients_without_pain_scores > 0;
  const hasSingleKneeImaging =
    data.summary?.patients_with_single_knee_imaging > 0;

  if (hasMissingPainScores || hasSingleKneeImaging) {
    html +=
      '<div style="margin: 20px 0; padding: 12px; background: #fff3cd; border-left: 4px solid #ff9800; border-radius: 4px;">';
    html += "<strong>⚠️ Reduced Confidence Warning:</strong><br>";

    const warnings = [];
    if (hasMissingPainScores) {
      warnings.push(
        `${data.summary.patients_without_pain_scores} patient(s) are missing pain scores (WOMAC/VAS). Predictions may be less precise.`
      );
    }
    if (hasSingleKneeImaging) {
      warnings.push(
        `${data.summary.patients_with_single_knee_imaging} patient(s) have single knee imaging. Predictions based on one knee only.`
      );
    }

    if (hasMissingPainScores && hasSingleKneeImaging) {
      html += `${data.summary.patients_without_pain_scores} patient(s) missing pain scores and ${data.summary.patients_with_single_knee_imaging} patient(s) with single knee imaging. `;
      html +=
        "Predictions for these patients may be less precise due to limited baseline data.";
    } else {
      html += warnings.join(" ");
    }

    html += "</div>";
  }

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
    html += '<canvas id="riskDistChart"></canvas>';
    html += "</div>";
  }

  // Validation metrics (if outcomes provided)
  if (data.validation_metrics) {
    html += '<div class="validation-metrics">';
    html += "<h3>Validation Metrics</h3>";

    if (data.validation_metrics.auc != null) {
      html += `<div class="metric-row">
              <span class="metric-label">AUC (Discrimination):</span>
              <span class="metric-value">${data.validation_metrics.auc.toFixed(
                3
              )}</span>
          </div>`;
    }

    if (data.validation_metrics.brier_score != null) {
      html += `<div class="metric-row">
              <span class="metric-label">Brier Score (Calibration):</span>
              <span class="metric-value">${data.validation_metrics.brier_score.toFixed(
                4
              )}</span>
          </div>`;
    }

    if (data.validation_metrics.event_rate != null) {
      html += `<div class="metric-row">
              <span class="metric-label">Event Rate:</span>
              <span class="metric-value">${data.validation_metrics.event_rate.toFixed(
                1
              )}%</span>
          </div>`;
    }

    if (data.validation_metrics.n_events != null) {
      html += `<div class="metric-row">
              <span class="metric-label">Number of Events:</span>
              <span class="metric-value">${data.validation_metrics.n_events}</span>
          </div>`;
    }

    html += "</div>";

    // ROC Curve
    if (data.plots.roc_curve) {
      html += '<div class="plot-container">';
      html += "<h3>ROC Curve</h3>";
      html += '<canvas id="rocChart"></canvas>';
      html += "</div>";
    }

    // Calibration Plot
    if (data.plots.calibration) {
      html += '<div class="plot-container">';
      html += "<h3>Calibration Plot</h3>";
      html += '<canvas id="calibrationChart"></canvas>';
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

  // Render charts
  renderCharts(data.plots);

  // NEW: Check if there are moderate/high-risk patients for outcome analysis
  const moderateHighRisk =
    data.summary.total_patients * (data.summary.high_risk_pct / 100);

  if (moderateHighRisk > 0) {
    const outcomeSection = document.getElementById("outcomeSection");
    const outcomeBtnText = document.getElementById("outcomeBtnText");

    if (outcomeSection && outcomeBtnText) {
      outcomeSection.style.display = "block";
      outcomeBtnText.textContent = `Analyze Expected Surgical Outcomes (${Math.round(
        moderateHighRisk
      )} patients)`;

      // Reset state
      window.outcomesPredicted = false;
      const outcomeResults = document.getElementById("outcomeResults");
      if (outcomeResults) {
        outcomeResults.style.display = "none";
      }
    }
  }
}

function renderCharts(plots) {
  // Risk Distribution Chart
  if (plots.risk_distribution && plots.risk_distribution.data) {
    const ctx = document.getElementById("riskDistChart");
    if (ctx) {
      new Chart(ctx, {
        type: "bar",
        data: {
          labels: plots.risk_distribution.data.labels,
          datasets: [
            {
              label: "Number of Patients",
              data: plots.risk_distribution.data.values,
              backgroundColor: "steelblue",
              borderColor: "black",
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: plots.risk_distribution.title,
              font: { size: 14, weight: "bold" },
            },
            legend: { display: false },
          },
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: plots.risk_distribution.ylabel,
              },
            },
            x: {
              title: {
                display: true,
                text: plots.risk_distribution.xlabel,
              },
            },
          },
        },
      });
    }
  }

  // ROC Curve
  if (plots.roc_curve && plots.roc_curve.data) {
    const ctx = document.getElementById("rocChart");
    if (ctx) {
      new Chart(ctx, {
        type: "line",
        data: {
          datasets: [
            {
              label: plots.roc_curve.data.model.label,
              data: plots.roc_curve.data.model.x.map((x, i) => ({
                x: x,
                y: plots.roc_curve.data.model.y[i],
              })),
              borderColor: "rgb(75, 192, 192)",
              backgroundColor: "rgba(75, 192, 192, 0.2)",
              borderWidth: 2,
              pointRadius: 0,
            },
            {
              label: plots.roc_curve.data.random.label,
              data: plots.roc_curve.data.random.x.map((x, i) => ({
                x: x,
                y: plots.roc_curve.data.random.y[i],
              })),
              borderColor: "rgb(255, 99, 132)",
              borderDash: [5, 5],
              borderWidth: 2,
              pointRadius: 0,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: plots.roc_curve.title,
              font: { size: 14, weight: "bold" },
            },
            legend: { display: true },
          },
          scales: {
            x: {
              type: "linear",
              min: 0,
              max: 1,
              title: {
                display: true,
                text: plots.roc_curve.xlabel,
              },
            },
            y: {
              type: "linear",
              min: 0,
              max: 1,
              title: {
                display: true,
                text: plots.roc_curve.ylabel,
              },
            },
          },
        },
      });
    }
  }

  // Calibration Plot
  if (plots.calibration && plots.calibration.data) {
    const ctx = document.getElementById("calibrationChart");
    if (ctx) {
      new Chart(ctx, {
        type: "scatter",
        data: {
          datasets: [
            {
              label: plots.calibration.data.model.label,
              data: plots.calibration.data.model.x.map((x, i) => ({
                x: x,
                y: plots.calibration.data.model.y[i],
              })),
              backgroundColor: "rgb(75, 192, 192)",
              borderColor: "rgb(75, 192, 192)",
              pointRadius: 6,
              showLine: true,
              tension: 0.4,
            },
            {
              label: plots.calibration.data.perfect.label,
              data: plots.calibration.data.perfect.x.map((x, i) => ({
                x: x,
                y: plots.calibration.data.perfect.y[i],
              })),
              borderColor: "rgb(255, 99, 132)",
              borderDash: [5, 5],
              borderWidth: 2,
              pointRadius: 0,
              showLine: true,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: plots.calibration.title,
              font: { size: 14, weight: "bold" },
            },
            legend: { display: true },
          },
          scales: {
            x: {
              type: "linear",
              min: 0,
              max: 1,
              title: {
                display: true,
                text: plots.calibration.xlabel,
              },
            },
            y: {
              type: "linear",
              min: 0,
              max: 1,
              title: {
                display: true,
                text: plots.calibration.ylabel,
              },
            },
          },
        },
      });
    }
  }
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

// Global variable to track if outcomes have been predicted
window.outcomesPredicted = false;

async function predictOutcomes() {
  if (!selectedFile || window.outcomesPredicted) return;

  const btn = document.getElementById("predictOutcomesBtn");
  const btnText = document.getElementById("outcomeBtnText");

  if (!btn || !btnText) return;

  btn.disabled = true;
  btnText.textContent = "Analyzing outcomes...";

  const formData = new FormData();
  formData.append("file", selectedFile);
  formData.append("run_outcome", "true");

  try {
    const response = await fetch("/api/validate", {
      method: "POST",
      body: formData,
    });

    const responseText = await response.text();

    if (!response.ok) {
      let errorMessage = `Server error (${response.status})`;
      try {
        const errorData = JSON.parse(responseText);
        errorMessage = errorData.error || errorMessage;
      } catch (e) {
        errorMessage = responseText || errorMessage;
      }
      alert("Error: " + errorMessage);
      return;
    }

    let data;
    try {
      data = JSON.parse(responseText);
    } catch (e) {
      alert("Error: Invalid response from server. Please try again.");
      console.error("JSON parse error:", e);
      return;
    }

    if (data.error) {
      alert("Error: " + data.error);
      return;
    }

    if (data.outcome_predictions) {
      if (data.outcome_predictions.error) {
        alert("Outcome prediction error: " + data.outcome_predictions.error);
      } else {
        displayOutcomeResults(data.outcome_predictions);
        window.outcomesPredicted = true;
        btnText.textContent = "✓ Outcomes Analyzed";
      }
    }
  } catch (error) {
    alert("Error predicting outcomes: " + error.message);
    console.error("Error:", error);
  } finally {
    btn.disabled = false;
  }
}

function displayOutcomeResults(outcomes) {
  const resultsDiv = document.getElementById("outcomeResults");
  if (!resultsDiv) return;

  let html = `
    <div class="outcome-results-container">
      <h3>Surgical Outcome Analysis</h3>
      
      <div class="metrics-grid">
        <div class="metric-card outcome-card">
          <div class="metric-value">${outcomes.n_analyzed}</div>
          <div class="metric-label">Patients Analyzed</div>
        </div>
        <div class="metric-card outcome-card">
          <div class="metric-value">${outcomes.mean_improvement.toFixed(
            1
          )}</div>
          <div class="metric-label">Mean Improvement (points)</div>
        </div>
        <div class="metric-card outcome-card">
          <div class="metric-value">${outcomes.median_improvement.toFixed(
            1
          )}</div>
          <div class="metric-label">Median Improvement (points)</div>
        </div>
        <div class="metric-card outcome-card">
          <div class="metric-value">±${outcomes.std_improvement.toFixed(
            1
          )}</div>
          <div class="metric-label">Std Deviation</div>
        </div>
      </div>
      
      <div class="plot-section">
        <h4>Expected Improvement Distribution</h4>
        <canvas id="improvementChart"></canvas>
        <p class="plot-caption">Distribution of expected WOMAC improvement across surgical candidates</p>
      </div>
      
      <div class="improvement-bands-table">
        <h4>Improvement Band Breakdown</h4>
        <table>
          <thead>
            <tr>
              <th>Improvement Band</th>
              <th>Number of Patients</th>
              <th>Percentage</th>
            </tr>
          </thead>
          <tbody>
  `;

  const totalPatients = outcomes.n_analyzed;
  const sortedBands = [
    "Likely Worse",
    "Minimal (0-10)",
    "Moderate (10-20)",
    "Good (20-30)",
    "Excellent (>30)",
  ];

  for (const band of sortedBands) {
    const count = outcomes.improvement_distribution[band] || 0;
    const pct = ((count / totalPatients) * 100).toFixed(1);

    html += `
      <tr>
        <td><strong>${band}</strong></td>
        <td>${count}</td>
        <td>${pct}%</td>
      </tr>
    `;
  }

  html += `
          </tbody>
        </table>
      </div>
      
      <div class="clinical-interpretation">
        <h4> Clinical Interpretation</h4>
        <div class="interpretation-box">
          <p><strong>WOMAC Improvement Scale:</strong></p>
          <ul>
            <li><strong>Minimal (0-10 points):</strong> Slight improvement, may not meet patient expectations</li>
            <li><strong>Moderate (10-20 points):</strong> Noticeable improvement, clinically significant</li>
            <li><strong>Good (20-30 points):</strong> Substantial improvement, strong surgical candidate</li>
            <li><strong>Excellent (>30 points):</strong> Exceptional improvement, ideal surgical candidate</li>
          </ul>
          <p><strong>Note:</strong> These predictions are based on OAI data and should be validated 
          against Bergman Clinics' surgical outcomes before clinical use.</p>
        </div>
      </div>
      
      <div class="download-section">
        <h4> Download Outcome Predictions</h4>
        <button class="btn-primary" onclick="downloadOutcomes()">
          Download CSV (Surgery Risk + Expected Outcomes)
        </button>
      </div>
    </div>
  `;

  resultsDiv.innerHTML = html;
  resultsDiv.style.display = "block";

  // Store CSV for download
  window.outcomeCSV = outcomes.csv;

  // Render improvement distribution chart
  if (outcomes.improvement_plot) {
    setTimeout(() => {
      renderImprovementChart(outcomes.improvement_plot);
    }, 100);
  }

  // Scroll to results
  resultsDiv.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderImprovementChart(plotData) {
  const ctx = document.getElementById("improvementChart");
  if (!ctx || !plotData || !plotData.data) return;

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: plotData.data.labels,
      datasets: [
        {
          label: plotData.ylabel,
          data: plotData.data.values,
          backgroundColor: [
            "#ef4444",
            "#f97316",
            "#eab308",
            "#22c55e",
            "#10b981",
          ],
          borderColor: "black",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: plotData.title,
          font: { size: 16, weight: "bold" },
        },
        legend: { display: false },
      },
      scales: {
        x: {
          title: {
            display: true,
            text: plotData.xlabel,
          },
        },
        y: {
          title: {
            display: true,
            text: plotData.ylabel,
          },
          beginAtZero: true,
        },
      },
    },
  });
}

function downloadOutcomes() {
  if (!window.outcomeCSV) {
    alert("No outcome predictions to download");
    return;
  }

  const blob = new Blob([window.outcomeCSV], { type: "text/csv" });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "doc_surgery_and_outcome_predictions.csv";
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

// ============================================================================
// Manual Entry Functions
// ============================================================================

// Patient batch storage
let patientBatch = [];

function showManualEntry() {
  document.getElementById("manualEntrySection").style.display = "block";
  document.getElementById("csvUploadSection").style.display = "none";
  document
    .querySelectorAll(".option-tab")
    .forEach((tab) => tab.classList.remove("active"));
  event.target.classList.add("active");
}

function showCsvUpload() {
  document.getElementById("manualEntrySection").style.display = "none";
  document.getElementById("csvUploadSection").style.display = "block";
  document
    .querySelectorAll(".option-tab")
    .forEach((tab) => tab.classList.remove("active"));
  event.target.classList.add("active");
}

// VAS to WOMAC conversion function
// Based on literature: Salaffi et al. 2003, Tubach et al. 2005
// Formula: WOMAC = (VAS × 8) + 15
function vasToWomac(vasScore, scale = "0-10") {
  if (scale === "0-100") {
    vasScore = vasScore / 10;
  }
  // Linear approximation: WOMAC ≈ 8×VAS + 15
  let womacApprox = vasScore * 8 + 15;
  // Clip to valid range (0-96)
  womacApprox = Math.max(0, Math.min(96, womacApprox));
  return womacApprox;
}

// Toggle between WOMAC and VAS input fields
function togglePainScoreType() {
  const painScoreType = document.querySelector(
    'input[name="painScoreType"]:checked'
  ).value;
  const womacRField = document.getElementById("womac_r_field");
  const womacLField = document.getElementById("womac_l_field");
  const vasRField = document.getElementById("vas_r_field");
  const vasLField = document.getElementById("vas_l_field");
  const vasInfo = document.getElementById("vasInfo");

  if (painScoreType === "vas") {
    // Show VAS fields, hide WOMAC fields
    womacRField.style.display = "none";
    womacLField.style.display = "none";
    vasRField.style.display = "block";
    vasLField.style.display = "block";
    vasInfo.style.display = "block";

    // Pain scores are optional - never required
    document.getElementById("vas_r").required = false;
    document.getElementById("vas_l").required = false;
    document.getElementById("womac_r").required = false;
    document.getElementById("womac_l").required = false;

    // Clear WOMAC fields
    document.getElementById("womac_r").value = "";
    document.getElementById("womac_l").value = "";
  } else if (painScoreType === "none") {
    // Hide all pain score fields
    womacRField.style.display = "none";
    womacLField.style.display = "none";
    vasRField.style.display = "none";
    vasLField.style.display = "none";
    vasInfo.style.display = "none";

    // Pain scores are optional - never required
    document.getElementById("vas_r").required = false;
    document.getElementById("vas_l").required = false;
    document.getElementById("womac_r").required = false;
    document.getElementById("womac_l").required = false;

    // Clear all fields
    document.getElementById("womac_r").value = "";
    document.getElementById("womac_l").value = "";
    document.getElementById("vas_r").value = "";
    document.getElementById("vas_l").value = "";
    document.getElementById("vas_r_womac").textContent = "--";
    document.getElementById("vas_l_womac").textContent = "--";
  } else {
    // Show WOMAC fields, hide VAS fields
    womacRField.style.display = "block";
    womacLField.style.display = "block";
    vasRField.style.display = "none";
    vasLField.style.display = "none";
    vasInfo.style.display = "none";

    // Pain scores are optional - never required
    document.getElementById("womac_r").required = false;
    document.getElementById("womac_l").required = false;
    document.getElementById("vas_r").required = false;
    document.getElementById("vas_l").required = false;

    // Clear VAS fields
    document.getElementById("vas_r").value = "";
    document.getElementById("vas_l").value = "";
    document.getElementById("vas_r_womac").textContent = "--";
    document.getElementById("vas_l_womac").textContent = "--";
  }
}

// Real-time VAS to WOMAC conversion display
document.getElementById("vas_r")?.addEventListener("input", function () {
  const vasValue = parseFloat(this.value);
  if (!isNaN(vasValue) && vasValue >= 0 && vasValue <= 10) {
    const womacEstimate = vasToWomac(vasValue);
    document.getElementById("vas_r_womac").textContent =
      womacEstimate.toFixed(1);
  } else {
    document.getElementById("vas_r_womac").textContent = "--";
  }
});

document.getElementById("vas_l")?.addEventListener("input", function () {
  const vasValue = parseFloat(this.value);
  if (!isNaN(vasValue) && vasValue >= 0 && vasValue <= 10) {
    const womacEstimate = vasToWomac(vasValue);
    document.getElementById("vas_l_womac").textContent =
      womacEstimate.toFixed(1);
  } else {
    document.getElementById("vas_l_womac").textContent = "--";
  }
});

// Form submission handler
document.getElementById("patientForm").addEventListener("submit", function (e) {
  e.preventDefault();

  // Validate KL grades - at least one must be available (not "Not available")
  const kl_r_value = document.getElementById("kl_r").value;
  const kl_l_value = document.getElementById("kl_l").value;

  // Check if both are "Not available" or empty
  if (
    (kl_r_value === "" || kl_r_value === "na") &&
    (kl_l_value === "" || kl_l_value === "na")
  ) {
    alert(
      "At least one knee must have imaging data. Both knees cannot be 'Not available'."
    );
    return;
  }

  // Parse KL grades (treat "na" as null)
  let kl_r = null;
  let kl_l = null;

  if (kl_r_value !== "" && kl_r_value !== "na") {
    kl_r = parseInt(kl_r_value);
    if (isNaN(kl_r) || kl_r < 0 || kl_r > 4) {
      alert("Invalid right knee KL grade. Please select a valid option.");
      return;
    }
  }

  if (kl_l_value !== "" && kl_l_value !== "na") {
    kl_l = parseInt(kl_l_value);
    if (isNaN(kl_l) || kl_l < 0 || kl_l > 4) {
      alert("Invalid left knee KL grade. Please select a valid option.");
      return;
    }
  }

  // Check that at least one knee has OA findings (KL ≥ 1) if both are available
  if (kl_r !== null && kl_l !== null) {
    if (kl_r === 0 && kl_l === 0) {
      alert(
        "At least one knee must have OA findings (KL grade ≥ 1). Both knees cannot be KL grade 0."
      );
      return;
    }
  }

  // Determine which pain score type is selected
  const painScoreType = document.querySelector(
    'input[name="painScoreType"]:checked'
  ).value;
  let womac_r = null;
  let womac_l = null;
  let vasUsed = false;
  let painScoresMissing = false;

  if (painScoreType === "vas") {
    // Convert VAS to WOMAC if provided
    const vas_r_str = document.getElementById("vas_r").value.trim();
    const vas_l_str = document.getElementById("vas_l").value.trim();

    if (vas_r_str !== "" || vas_l_str !== "") {
      // At least one VAS provided - validate those that are provided
      if (vas_r_str !== "") {
        const vas_r = parseFloat(vas_r_str);
        if (isNaN(vas_r) || vas_r < 0 || vas_r > 10) {
          alert(
            "Please enter a valid VAS score (0-10) for right knee, or leave empty."
          );
          return;
        }
        womac_r = vasToWomac(vas_r);
        vasUsed = true;
      }

      if (vas_l_str !== "") {
        const vas_l = parseFloat(vas_l_str);
        if (isNaN(vas_l) || vas_l < 0 || vas_l > 10) {
          alert(
            "Please enter a valid VAS score (0-10) for left knee, or leave empty."
          );
          return;
        }
        womac_l = vasToWomac(vas_l);
        vasUsed = true;
      }
    } else {
      // No VAS provided
      painScoresMissing = true;
    }
  } else if (painScoreType === "womac") {
    // Use WOMAC directly if provided
    const womac_r_str = document.getElementById("womac_r").value.trim();
    const womac_l_str = document.getElementById("womac_l").value.trim();

    if (womac_r_str !== "" || womac_l_str !== "") {
      // At least one WOMAC provided - validate those that are provided
      if (womac_r_str !== "") {
        womac_r = parseFloat(womac_r_str);
        if (isNaN(womac_r) || womac_r < 0 || womac_r > 96) {
          alert(
            "Please enter a valid WOMAC score (0-96) for right knee, or leave empty."
          );
          return;
        }
      }

      if (womac_l_str !== "") {
        womac_l = parseFloat(womac_l_str);
        if (isNaN(womac_l) || womac_l < 0 || womac_l > 96) {
          alert(
            "Please enter a valid WOMAC score (0-96) for left knee, or leave empty."
          );
          return;
        }
      }
    } else {
      // No WOMAC provided
      painScoresMissing = true;
    }
  } else {
    // painScoreType === "none" - no pain scores
    painScoresMissing = true;
  }

  // Family history is optional - default to 0 (No) if not specified
  const famHxValue = document.getElementById("fam_hx").value;
  const fam_hx = famHxValue !== "" ? parseInt(famHxValue) : 0;

  const patient = {
    age: parseFloat(document.getElementById("age").value),
    sex: parseInt(document.getElementById("sex").value),
    bmi: parseFloat(document.getElementById("bmi").value),
    womac_r: womac_r, // Can be null
    womac_l: womac_l, // Can be null
    kl_r: kl_r, // Can be null if "Not available"
    kl_l: kl_l, // Can be null if "Not available"
    fam_hx: fam_hx,
    _pain_scores_missing: painScoresMissing, // Flag for display
    _kl_missing: kl_r === null || kl_l === null, // Flag for display
  };

  // Store VAS info for display if VAS was used
  if (vasUsed) {
    patient._vas_used = true;
    const vas_r_str = document.getElementById("vas_r").value.trim();
    const vas_l_str = document.getElementById("vas_l").value.trim();
    patient._vas_r = vas_r_str !== "" ? parseFloat(vas_r_str) : null;
    patient._vas_l = vas_l_str !== "" ? parseFloat(vas_l_str) : null;
  }

  // Add patient_id if provided (for display purposes only, not sent to API)
  const patientId = document.getElementById("patientId").value.trim();
  if (patientId) {
    patient._patient_id = patientId; // Internal tracking only
  }

  // Add optional outcome if provided
  const outcome = document.getElementById("tkr_outcome").value;
  if (outcome !== "") {
    patient.tkr_outcome = parseInt(outcome);
  }

  // Check for duplicate patient ID
  if (patientId && patientBatch.find((p) => p._patient_id === patientId)) {
    alert("Patient ID already exists. Please use a unique ID.");
    return;
  }

  // Add to batch
  patientBatch.push(patient);

  // Update display
  updatePatientList();

  // Clear form
  clearForm();

  // Show success message
  const displayId = patientId || `Patient ${patientBatch.length}`;
  showNotification(`${displayId} added`);
});

function updatePatientList() {
  const listDiv = document.getElementById("patientList");
  const cardsDiv = document.getElementById("patientCards");
  const countSpan = document.getElementById("patientCount");

  if (patientBatch.length === 0) {
    listDiv.style.display = "none";
    return;
  }

  listDiv.style.display = "block";
  countSpan.textContent = patientBatch.length;

  cardsDiv.innerHTML = patientBatch
    .map((p, index) => {
      const displayId = p._patient_id || `Patient ${index + 1}`;
      let painScoreNote = "";
      if (p._vas_used) {
        const vasR = p._vas_r !== null ? p._vas_r.toFixed(1) : "N/A";
        const vasL = p._vas_l !== null ? p._vas_l.toFixed(1) : "N/A";
        painScoreNote = `<br><small style="color: #666;">WOMAC estimated from VAS (R: ${vasR}, L: ${vasL})</small>`;
      } else if (p._pain_scores_missing) {
        painScoreNote = `<br><small style="color: #ff9800;">⚠️ No pain scores - reduced confidence</small>`;
      }

      const womacDisplay =
        p.womac_r !== null && p.womac_l !== null
          ? `WOMAC: R=${p.womac_r.toFixed(1)}, L=${p.womac_l.toFixed(1)}`
          : p.womac_r !== null
          ? `WOMAC: R=${p.womac_r.toFixed(1)}, L=N/A`
          : p.womac_l !== null
          ? `WOMAC: R=N/A, L=${p.womac_l.toFixed(1)}`
          : `WOMAC: Not provided`;

      // KL grade display
      const kl_r_display = p.kl_r !== null ? p.kl_r : "N/A";
      const kl_l_display = p.kl_l !== null ? p.kl_l : "N/A";
      let klNote = "";
      if (p._kl_missing) {
        klNote = `<br><small style="color: #ff9800;">⚠️ Single knee imaging - reduced confidence</small>`;
      }

      return `
        <div class="patient-card">
            <div class="patient-card-header">
                <strong>${displayId}</strong>
                <button class="btn-remove" onclick="removePatient(${index})" title="Remove patient">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                </button>
            </div>
            <div class="patient-card-body">
                Age: ${p.age}, Sex: ${
        p.sex === 1 ? "M" : "F"
      }, BMI: ${p.bmi.toFixed(1)}
                <br>
                ${womacDisplay}${painScoreNote}
                <br>
                KL Grade: R=${kl_r_display}, L=${kl_l_display}${klNote}
            </div>
        </div>
    `;
    })
    .join("");
}

function removePatient(index) {
  const patient = patientBatch[index];
  const displayId = patient._patient_id || `Patient ${index + 1}`;
  if (confirm(`Remove ${displayId}?`)) {
    patientBatch.splice(index, 1);
    updatePatientList();
    showNotification(`${displayId} removed`);
  }
}

function clearForm() {
  // Reset pain score type to WOMAC
  document.querySelector(
    'input[name="painScoreType"][value="womac"]'
  ).checked = true;
  togglePainScoreType();
  document.getElementById("patientForm").reset();
  // Reset pain score type after form reset (since reset clears radio buttons)
  document.querySelector(
    'input[name="painScoreType"][value="womac"]'
  ).checked = true;
  togglePainScoreType();
  document.getElementById("age").focus();
}

// Initialize form on page load - ensure WOMAC is selected and required
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", function () {
    // Ensure WOMAC is selected by default
    const womacRadio = document.querySelector(
      'input[name="painScoreType"][value="womac"]'
    );
    if (womacRadio) {
      womacRadio.checked = true;
      togglePainScoreType();
    }
  });
} else {
  // DOM already loaded
  const womacRadio = document.querySelector(
    'input[name="painScoreType"][value="womac"]'
  );
  if (womacRadio) {
    womacRadio.checked = true;
    togglePainScoreType();
  }
}

function clearAllPatients() {
  if (patientBatch.length === 0) return;

  if (confirm(`Clear all ${patientBatch.length} patients?`)) {
    patientBatch = [];
    updatePatientList();
    showNotification("All patients cleared");
  }
}

async function analyzeBatch() {
  if (patientBatch.length === 0) {
    alert("Please add at least one patient first.");
    return;
  }

  document.getElementById("loading").style.display = "flex";

  try {
    // Convert batch to CSV - exclude internal _patient_id field
    // Convert KL grade null to "na" string for CSV
    const csvHeaders = [
      "age",
      "sex",
      "bmi",
      "womac_r",
      "womac_l",
      "kl_r",
      "kl_l",
      "fam_hx",
    ];

    // Add tkr_outcome if any patient has it
    const hasOutcome = patientBatch.some((p) => p.tkr_outcome !== undefined);
    if (hasOutcome) {
      csvHeaders.push("tkr_outcome");
    }

    const csv = [
      csvHeaders.join(","),
      ...patientBatch.map((p) =>
        csvHeaders
          .map((h) => {
            const value = p[h];
            // Handle null/undefined for optional fields
            if (value === null || value === undefined) {
              // For KL grades, use "na" string to indicate "Not available"
              if (h === "kl_r" || h === "kl_l") {
                return "na";
              }
              return "";
            }
            return value;
          })
          .join(",")
      ),
    ].join("\n");

    // Create blob and send like CSV upload
    const blob = new Blob([csv], { type: "text/csv" });
    const formData = new FormData();
    formData.append("file", blob, "manual_entry.csv");

    const response = await fetch("/api/validate", {
      method: "POST",
      body: formData,
    });

    const responseText = await response.text();
    let data;

    try {
      data = JSON.parse(responseText);
    } catch (e) {
      throw new Error(
        `Server error: ${response.status} ${responseText.substring(0, 100)}`
      );
    }

    document.getElementById("loading").style.display = "none";

    if (data.error) {
      alert("Error: " + data.error);
      return;
    }

    displayResults(data);
  } catch (error) {
    document.getElementById("loading").style.display = "none";
    alert("Error analyzing patients: " + error.message);
  }
}

function showNotification(message) {
  const notification = document.createElement("div");
  notification.className = "notification";
  notification.textContent = message;
  document.body.appendChild(notification);

  setTimeout(() => {
    notification.classList.add("show");
  }, 100);

  setTimeout(() => {
    notification.classList.remove("show");
    setTimeout(() => notification.remove(), 300);
  }, 2000);
}
