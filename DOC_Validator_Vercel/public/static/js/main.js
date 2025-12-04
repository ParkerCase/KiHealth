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

// Form submission handler
document.getElementById("patientForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const patient = {
    age: parseFloat(document.getElementById("age").value),
    sex: parseInt(document.getElementById("sex").value),
    bmi: parseFloat(document.getElementById("bmi").value),
    womac_r: parseFloat(document.getElementById("womac_r").value),
    womac_l: parseFloat(document.getElementById("womac_l").value),
    kl_r: parseInt(document.getElementById("kl_r").value),
    kl_l: parseInt(document.getElementById("kl_l").value),
    fam_hx: parseInt(document.getElementById("fam_hx").value),
  };

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
                WOMAC: R=${p.womac_r.toFixed(1)}, L=${p.womac_l.toFixed(1)}
                <br>
                KL Grade: R=${p.kl_r}, L=${p.kl_l}
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
  document.getElementById("patientForm").reset();
  document.getElementById("age").focus();
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
      ...patientBatch.map((p) => csvHeaders.map((h) => p[h] ?? "").join(",")),
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
