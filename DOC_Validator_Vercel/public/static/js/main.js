// DOC Validator - Main JavaScript

// API Configuration - Use Railway backend URL
// In production (Vercel), this will be the Railway API URL
// In development, use relative URLs for local testing
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? '' // Use relative URLs for local development
  : 'https://doc-production-5888.up.railway.app'; // Railway API URL for production

// CSV upload functionality removed - manual entry only

// analyzeData function removed - now handled directly in form submission

function displayResults(data) {
  // Check if we're on mobile (mobile form is visible)
  const isMobile = window.innerWidth <= 768;
  const mobileForm = document.getElementById("mobilePatientForm");
  const isMobileFormVisible = mobileForm && window.getComputedStyle(mobileForm).display !== "none";
  
  let resultsDiv;
  if (isMobileFormVisible) {
    // Mobile: show results in Step 4
    resultsDiv = document.getElementById("mobileResults");
    // Hide desktop results
    const desktopResults = document.getElementById("results");
    if (desktopResults) desktopResults.style.display = "none";
    // Navigate to step 4
    if (currentMobileStep !== 4) {
      // Hide current step
      const currentStepEl = document.getElementById(`mobileStep${currentMobileStep}`);
      if (currentStepEl) currentStepEl.classList.remove("active");
      currentMobileStep = 4;
      const step4El = document.getElementById("mobileStep4");
      if (step4El) step4El.classList.add("active");
      updateMobileStepIndicators();
      updateMobileStepVisibility();
    }
    } else {
    // Desktop: show results in desktop results div
    resultsDiv = document.getElementById("results");
    // Hide mobile results
    const mobileResults = document.getElementById("mobileResults");
    if (mobileResults) mobileResults.innerHTML = "";
  }
  
  if (!resultsDiv) {
    console.error("Results div not found");
      return;
    }

  // Only add title if on desktop (mobile already has it in step header)
  let html = "";
  if (!isMobileFormVisible) {
    html = "<h2>Analysis Results</h2>";
  }

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
        `${data.summary.patients_without_pain_scores} patient(s) are missing symptom assessments. Predictions may be less precise.`
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

  // Check if single patient mode
  const isSinglePatient = data.summary.total_patients === 1;
  
  // NEW ORDER: Show Outcomes FIRST (if available), then Risk SECOND
  // Check if outcome predictions are already in the response
  if (data.outcome_predictions && !data.outcome_predictions.error) {
    // Display outcomes FIRST - most prominent
    html += '<div id="outcomeResultsInline" style="margin: 30px 0;"></div>';
  }
  
  // Summary statistics - Surgery Risk SECOND (less prominent)
  html += '<div class="summary-stats" style="margin-top: 50px; padding-top: 30px; border-top: 2px solid #e2e8f0;">';
  html += '<h3 style="font-size: 1.5rem; font-weight: 600; color: #475569; margin-bottom: 20px;">Surgery Risk Assessment</h3>';
  if (isSinglePatient) {
    // Single patient: Show risk smaller and less prominent
    html += `<div class="stat-card" style="grid-column: 1 / -1; max-width: 350px; margin: 0 auto; border: 2px solid #e2e8f0; border-radius: 16px; padding: 24px; background: #f8fafc; box-shadow: 0 2px 8px rgba(0,0,0,0.05);" title="Probability of needing TKR within 4 years">
        <div class="stat-value" style="font-size: 2.5rem; color: #64748b; font-weight: 600;">${data.summary.avg_risk.toFixed(1)}%</div>
        <div class="stat-label" style="font-size: 1rem; margin-top: 10px; color: #475569; font-weight: 600;">Surgery Risk</div>
        <div style="font-size: 0.85rem; color: #64748b; margin-top: 8px;">Probability of needing TKR within 4 years</div>
    </div>`;
  } else {
    // Multiple patients: Show batch stats
  html += `<div class="stat-card">
        <div class="stat-value">${data.summary.total_patients}</div>
        <div class="stat-label">Total Patients</div>
    </div>`;
    html += `<div class="stat-card" title="Average probability of needing TKR within 4 years">
        <div class="stat-value">${data.summary.avg_risk.toFixed(1)}%</div>
        <div class="stat-label">Average Risk</div>
        <div style="font-size: 0.7rem; color: #64748b; margin-top: 4px;">Probability of TKR</div>
    </div>`;
    html += `<div class="stat-card" title="Patients with ≥20% probability of needing TKR within 4 years">
        <div class="stat-value">${data.summary.high_risk_count}</div>
        <div class="stat-label">High Risk Patients</div>
        <div style="font-size: 0.7rem; color: #64748b; margin-top: 4px;">≥20% probability</div>
    </div>`;
    html += `<div class="stat-card" title="Percentage of patients with high risk (≥20%)">
        <div class="stat-value">${data.summary.high_risk_pct.toFixed(1)}%</div>
        <div class="stat-label">High Risk %</div>
        <div style="font-size: 0.7rem; color: #64748b; margin-top: 4px;">≥20% threshold</div>
    </div>`;
  }
  html += "</div>";

  // Risk distribution plot - only for multiple patients
  if (!isSinglePatient && data.plots.risk_distribution) {
    html += '<div class="plot-container">';
    html += "<h3>Risk Distribution</h3>";
    html += '<canvas id="riskDistChart"></canvas>';
    html += "</div>";
  }

  // Validation metrics (if outcomes provided) - only for multiple patients
  if (!isSinglePatient && data.validation_metrics) {
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

  // Download section - only for multiple patients
  if (!isSinglePatient) {
  html += '<div class="download-section">';
  html += "<h3>Download Predictions</h3>";
  html += "<p>Download the predictions as a CSV file</p>";
  html +=
    '<button class="download-btn" onclick="downloadPredictions()">Download CSV</button>';
  html += "</div>";
  }

  resultsDiv.innerHTML = html;
  resultsDiv.style.display = "block";

  // Store predictions CSV for download
  window.predictionsCSV = data.predictions_csv;

  // Render charts
  renderCharts(data.plots);

  // NEW ORDER: Display outcomes FIRST if they exist in the response
  if (data.outcome_predictions && !data.outcome_predictions.error) {
    // Display outcomes inline in results (FIRST, most prominent)
    const outcomeResultsInline = document.getElementById("outcomeResultsInline");
    if (outcomeResultsInline) {
      displayOutcomeResultsInline(data.outcome_predictions, outcomeResultsInline);
    }
  }
}

// Display outcomes inline (for when they come with the initial response)
function displayOutcomeResultsInline(outcomes, container) {
  if (!container) return;

  // Use success metrics if available, fallback to old format
  const hasSuccessMetrics = outcomes.success_distribution !== undefined;
  const successRate = outcomes.success_rate || 0;
  const meanSuccessProb = outcomes.mean_success_probability || 0;
  const medianSuccessProb = outcomes.median_success_probability || 0;
  
  // Check if single patient mode
  const patientOutcomes = outcomes.patient_outcomes || [];
  const isSinglePatient = patientOutcomes.length === 1;
  
  let html = `
    <div class="outcome-results-container" style="margin-bottom: 40px; padding: 32px; background: #ffffff; border-radius: 20px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
      <h3 style="font-size: 2rem; font-weight: 700; color: #1e293b; margin-bottom: 8px; border-bottom: 3px solid #3b82f6; padding-bottom: 12px;">Expected Surgical Outcomes</h3>
  `;
  
  if (isSinglePatient) {
    // Single patient: Show individual results prominently
    const patient = patientOutcomes[0];
    const improvement = patient._womac_improvement || 0;
    const successProb = patient.success_probability || 0;
    
    html += `
      <div style="max-width: 600px; margin: 0 auto; padding-top: 20px;">
        <div class="metric-card outcome-card highlight-card" style="border: 3px solid #3b82f6; margin-bottom: 24px; background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%); padding: 32px; border-radius: 16px; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);">
          <div class="metric-value" style="font-size: 4rem; color: #1e40af; margin-bottom: 12px; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">${improvement.toFixed(1)}</div>
          <div class="metric-label" style="font-size: 1.3rem; margin-bottom: 10px; color: #1e293b; font-weight: 600;">Expected Improvement (points)</div>
          <div style="font-size: 1rem; color: #475569; font-weight: 500; margin-bottom: 4px;">WOMAC/Function/Pain improvement</div>
          <div style="font-size: 0.85rem; color: #64748b; margin-top: 8px; font-style: italic;">±15 points typical uncertainty</div>
          ${improvement >= 30 
            ? `<div style="margin-top: 16px; padding: 14px; background: #d1fae5; border-radius: 10px; color: #065f46; font-weight: 700; border: 2px solid #10b981; font-size: 1rem;">
                ✓ Meets success threshold (≥30 points)
              </div>`
            : `<div style="margin-top: 16px; padding: 14px; background: #fee2e2; border-radius: 10px; color: #991b1b; font-weight: 700; border: 2px solid #ef4444; font-size: 1rem;">
                Below threshold (needs ${(30 - improvement).toFixed(1)} more points)
              </div>`}
        </div>
        
        <div class="metric-card outcome-card" style="margin-bottom: 20px; background: linear-gradient(135deg, #ffffff 0%, #fef3c7 100%); padding: 28px; border-radius: 16px; border: 2px solid #fde68a; box-shadow: 0 4px 12px rgba(234, 179, 8, 0.15);">
          <div class="metric-value" style="font-size: 3rem; color: ${patient.success_category.includes('Excellent') || patient.success_category.includes('Successful') ? '#1e40af' : patient.success_category.includes('Moderate') ? '#b45309' : '#c2410c'}; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 8px;">
            ${successProb.toFixed(1)}%
          </div>
          <div class="metric-label" style="font-size: 1.2rem; color: #1e293b; font-weight: 600; margin-bottom: 6px;">Success Probability</div>
          <div style="font-size: 0.95rem; color: #475569; margin-top: 8px; font-weight: 500;">${patient.success_category}</div>
        </div>
      </div>
    `;
  } else {
    // Multiple patients: Show batch metrics (keep existing code)
    const avgImprovement = patientOutcomes.length > 0
      ? patientOutcomes.reduce((sum, p) => sum + (p._womac_improvement || 0), 0) / patientOutcomes.length
      : 0;
    
    html += `
      <div class="metrics-grid" style="margin-top: 20px;">
        <div class="metric-card outcome-card highlight-card" style="border: 3px solid #3b82f6;">
          <div class="metric-value" style="font-size: 2.5rem; color: #3b82f6;">${avgImprovement.toFixed(1)}</div>
          <div class="metric-label">Average Expected Improvement (points)</div>
          <div style="font-size: 0.85rem; color: #64748b; margin-top: 4px;">WOMAC/Function/Pain improvement</div>
        </div>
        <div class="metric-card outcome-card">
          <div class="metric-value">${outcomes.n_analyzed}</div>
          <div class="metric-label">Patients Analyzed</div>
        </div>
        <div class="metric-card outcome-card highlight-card">
          <div class="metric-value">${successRate.toFixed(1)}%</div>
          <div class="metric-label">Success Rate (≥30 improvement)</div>
        </div>
        <div class="metric-card outcome-card">
          <div class="metric-value">${meanSuccessProb.toFixed(1)}%</div>
          <div class="metric-label">Mean Success Probability</div>
        </div>
        <div class="metric-card outcome-card">
          <div class="metric-value">${medianSuccessProb.toFixed(1)}%</div>
          <div class="metric-label">Median Success Probability</div>
        </div>
      </div>
    `;
  }
  
  html += `
      <div class="success-category-legend" style="margin-top: 30px; padding-top: 24px; border-top: 2px solid #e2e8f0;">
        <p class="legend-note" style="font-size: 0.9em; color: #475569; font-weight: 500;">
          <strong>Success Definition:</strong> A successful outcome is defined as ≥30 points improvement in symptoms and function.
          Categories are based on validated clinical outcome measures.
        </p>
        <p class="legend-note" style="margin-top: 8px; font-size: 0.9em; color: #475569; font-weight: 500;">
          <strong>Note:</strong> These predictions are based on 379 OAI surgical patients. Model explains 41% of variance (R²=0.41) with ±15 point typical uncertainty. Should be validated against Bergman Clinics' surgical outcomes before clinical use.
        </p>
      </div>
    </div>
  `;
  
  container.innerHTML = html;
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
  a.download = "DOC_Surgery_Risk_Predictions.csv";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}

// Global variable to track if outcomes have been predicted
window.outcomesPredicted = false;

async function predictOutcomes() {
  if (window.outcomesPredicted) return;

  const btn = document.getElementById("predictOutcomesBtn");
  const btnText = document.getElementById("outcomeBtnText");

  if (!btn || !btnText) return;

  btn.disabled = true;
  btnText.textContent = "Analyzing outcomes...";

  const formData = new FormData();
  
  // Handle manual entry (CSV upload removed)
  if (patientBatch && patientBatch.length > 0) {
    // Manual entry path - convert batch to CSV
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
            if (value === null || value === undefined) {
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
    
    const blob = new Blob([csv], { type: "text/csv" });
    formData.append("file", blob, "manual_entry.csv");
  } else {
    alert("No patients to analyze. Please add patients or upload a CSV file.");
    btn.disabled = false;
    btnText.textContent = "Analyze Expected Surgical Outcomes";
    return;
  }
  
  formData.append("run_outcome", "true");

  try {
    const response = await fetch(`${API_BASE_URL}/api/validate`, {
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

    // Outcomes are now displayed inline in displayResults, not separately
    if (data.outcome_predictions && data.outcome_predictions.error) {
        alert("Outcome prediction error: " + data.outcome_predictions.error);
    }
  } catch (error) {
    console.error("Error predicting outcomes:", error);
    if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
      alert("Error: Cannot connect to API server. Please check:\n1. Railway server is running\n2. API URL is correct: " + API_BASE_URL);
    } else {
      alert("Error predicting outcomes: " + error.message);
    }
    btn.disabled = false;
    btnText.textContent = "Analyze Expected Surgical Outcomes";
  }
}

function displayOutcomeResults(outcomes) {
  const resultsDiv = document.getElementById("outcomeResults");
  if (!resultsDiv) return;

  // Use success metrics if available, fallback to old format
  const hasSuccessMetrics = outcomes.success_distribution !== undefined;
  const successRate = outcomes.success_rate || 0;
  const meanSuccessProb = outcomes.mean_success_probability || 0;
  const medianSuccessProb = outcomes.median_success_probability || 0;
  
  // Check if single patient mode
  const patientOutcomes = outcomes.patient_outcomes || [];
  const isSinglePatient = patientOutcomes.length === 1;

  let html = `
    <div class="outcome-results-container">
      <h3>Expected Surgical Outcomes</h3>
  `;
  
  if (isSinglePatient) {
    // Single patient: Show individual results prominently
    const patient = patientOutcomes[0];
    const improvement = patient._womac_improvement || 0;
    const successProb = patient.success_probability || 0;
    
    html += `
      <div style="max-width: 600px; margin: 0 auto;">
        <div class="metric-card outcome-card highlight-card" style="border: 3px solid #3b82f6; margin-bottom: 30px; background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%);">
          <div class="metric-value" style="font-size: 4rem; color: #1e40af; margin-bottom: 10px; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">${improvement.toFixed(1)}</div>
          <div class="metric-label" style="font-size: 1.3rem; margin-bottom: 8px; color: #1e293b; font-weight: 600;">Expected Improvement (points)</div>
          <div style="font-size: 1rem; color: #475569; font-weight: 500;">WOMAC/Function/Pain improvement</div>
          <div style="font-size: 0.85rem; color: #64748b; margin-top: 8px; font-style: italic;">±15 points typical uncertainty</div>
          ${improvement >= 30 
            ? `<div style="margin-top: 15px; padding: 12px; background: #d1fae5; border-radius: 8px; color: #065f46; font-weight: 700; border: 2px solid #10b981; font-size: 1rem;">
                ✓ Meets success threshold (≥30 points)
              </div>`
            : `<div style="margin-top: 15px; padding: 12px; background: #fee2e2; border-radius: 8px; color: #991b1b; font-weight: 700; border: 2px solid #ef4444; font-size: 1rem;">
                Below threshold (needs ${(30 - improvement).toFixed(1)} more points)
              </div>`}
        </div>
        
        <div class="metric-card outcome-card" style="margin-bottom: 20px; background: linear-gradient(135deg, #ffffff 0%, #fef3c7 100%);">
          <div class="metric-value" style="font-size: 3rem; color: ${patient.success_category.includes('Excellent') || patient.success_category.includes('Successful') ? '#1e40af' : patient.success_category.includes('Moderate') ? '#b45309' : '#c2410c'}; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            ${successProb.toFixed(1)}%
          </div>
          <div class="metric-label" style="font-size: 1.2rem; color: #1e293b; font-weight: 600;">Success Probability</div>
          <div style="font-size: 0.95rem; color: #475569; margin-top: 8px; font-weight: 500;">${patient.success_category}</div>
        </div>
      </div>
    `;
  } else {
    // Multiple patients: Show batch metrics
    const avgImprovement = patientOutcomes.length > 0
      ? patientOutcomes.reduce((sum, p) => sum + (p._womac_improvement || 0), 0) / patientOutcomes.length
      : 0;
    
    html += `
      <div class="metrics-grid">
        <div class="metric-card outcome-card highlight-card" style="border: 3px solid #3b82f6;">
          <div class="metric-value" style="font-size: 2.5rem; color: #3b82f6;">${avgImprovement.toFixed(1)}</div>
          <div class="metric-label">Average Expected Improvement (points)</div>
          <div style="font-size: 0.85rem; color: #64748b; margin-top: 4px;">WOMAC/Function/Pain improvement</div>
        </div>
        <div class="metric-card outcome-card">
          <div class="metric-value">${outcomes.n_analyzed}</div>
          <div class="metric-label">Patients Analyzed</div>
        </div>
        <div class="metric-card outcome-card highlight-card">
          <div class="metric-value">${successRate.toFixed(1)}%</div>
          <div class="metric-label">Success Rate (≥30 improvement)</div>
        </div>
        <div class="metric-card outcome-card">
          <div class="metric-value">${meanSuccessProb.toFixed(1)}%</div>
          <div class="metric-label">Mean Success Probability</div>
        </div>
        <div class="metric-card outcome-card">
          <div class="metric-value">${medianSuccessProb.toFixed(1)}%</div>
          <div class="metric-label">Median Success Probability</div>
        </div>
      </div>
      
      <div class="plot-section">
        <h4>Surgical Success Category Distribution</h4>
        <canvas id="improvementChart"></canvas>
        <p class="plot-caption">Distribution of expected surgical success categories across patients</p>
      </div>
      
      <div class="improvement-bands-table">
        <h4>Success Category Breakdown</h4>
        <table>
          <thead>
            <tr>
              <th>Success Category</th>
              <th>Expected Improvement</th>
              <th>Number of Patients</th>
              <th>Percentage</th>
              <th>Success Probability</th>
            </tr>
          </thead>
          <tbody>
  `;

  const totalPatients = outcomes.n_analyzed;
  const categoryOrder = [
    "Excellent Outcome",
    "Successful Outcome",
    "Moderate Improvement",
    "Limited Improvement",
    "Minimal Improvement",
  ];

  // Category color mapping
  const categoryColors = {
    "Excellent Outcome": "text-green-600",
    "Successful Outcome": "text-blue-600",
    "Moderate Improvement": "text-yellow-600",
    "Limited Improvement": "text-orange-600",
    "Minimal Improvement": "text-red-600",
  };

  const categoryProbRanges = {
    "Excellent Outcome": "85-100%",
    "Successful Outcome": "70-85%",
    "Moderate Improvement": "40-70%",
    "Limited Improvement": "20-40%",
    "Minimal Improvement": "0-20%",
  };
    
    const categoryImprovementRanges = {
      "Excellent Outcome": "≥40 points",
      "Successful Outcome": "30-39 points",
      "Moderate Improvement": "20-29 points",
      "Limited Improvement": "10-19 points",
      "Minimal Improvement": "<10 points",
  };

  const distribution = hasSuccessMetrics 
    ? outcomes.success_distribution 
    : outcomes.improvement_distribution || {};

  for (const category of categoryOrder) {
    const count = distribution[category] || 0;
    const pct = totalPatients > 0 ? ((count / totalPatients) * 100).toFixed(1) : "0.0";
    const colorClass = categoryColors[category] || "";
    const probRange = categoryProbRanges[category] || "";
      const improvementRange = categoryImprovementRanges[category] || "";

    html += `
      <tr>
        <td><strong class="${colorClass}">${category}</strong></td>
          <td><strong>${improvementRange}</strong></td>
        <td>${count}</td>
        <td>${pct}%</td>
        <td>${probRange}</td>
      </tr>
    `;
  }

  html += `
          </tbody>
        </table>
      </div>
      
      <div class="success-category-legend">
        <h4>Outcome Categories</h4>
        <div class="legend-grid">
          <div class="legend-item">
            <div class="legend-color" style="background-color: #10b981;"></div>
            <div class="legend-content">
              <span class="legend-category">Excellent Outcome</span>
              <span class="legend-description">Substantial improvement expected (85-100% success probability)</span>
            </div>
          </div>
          <div class="legend-item">
            <div class="legend-color" style="background-color: #3b82f6;"></div>
            <div class="legend-content">
              <span class="legend-category">Successful Outcome</span>
              <span class="legend-description">Significant improvement expected (70-85% success probability)</span>
            </div>
          </div>
          <div class="legend-item">
            <div class="legend-color" style="background-color: #eab308;"></div>
            <div class="legend-content">
              <span class="legend-category">Moderate Improvement</span>
              <span class="legend-description">Noticeable improvement expected (40-70% success probability)</span>
            </div>
          </div>
          <div class="legend-item">
            <div class="legend-color" style="background-color: #f97316;"></div>
            <div class="legend-content">
              <span class="legend-category">Limited Improvement</span>
              <span class="legend-description">Some improvement expected (20-40% success probability)</span>
            </div>
          </div>
          <div class="legend-item">
            <div class="legend-color" style="background-color: #ef4444;"></div>
            <div class="legend-content">
              <span class="legend-category">Minimal Improvement</span>
              <span class="legend-description">Limited improvement expected (0-20% success probability)</span>
            </div>
          </div>
        </div>
        <p class="legend-note">
          <strong>Success Definition:</strong> A successful outcome is defined as ≥30 points improvement in symptoms and function.
          Categories are based on validated clinical outcome measures.
        </p>
        <p class="legend-note" style="margin-top: 8px; font-size: 0.9em; color: #666;">
            <strong>Note:</strong> These predictions are based on 379 OAI surgical patients. Model explains 41% of variance (R²=0.41) with ±15 point typical uncertainty. Should be validated against Bergman Clinics' surgical outcomes before clinical use.
        </p>
      </div>
      
      <div class="filters-and-sort-section" style="margin-top: 30px;">
        <h4>Filter & Sort Patients by Outcome</h4>
        <div class="filters-container" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
          <!-- Filter Controls -->
          <div class="filter-panel" style="background: #f7fafc; padding: 20px; border-radius: 8px; border: 2px solid #e2e8f0;">
            <h5 style="margin-bottom: 15px; font-weight: 600;">Filter by Outcome</h5>
            
            <!-- Success Category Filter -->
            <div style="margin-bottom: 15px;">
              <label style="display: block; font-weight: 500; margin-bottom: 8px; font-size: 0.9rem;">
                Expected Outcome Categories:
              </label>
              <div style="display: flex; flex-direction: column; gap: 6px;">
                ${categoryOrder.map(category => {
                  const colorClass = categoryColors[category] || "";
                  return `
                  <label style="display: flex; align-items: center; cursor: pointer; padding: 4px;">
                    <input type="checkbox" class="outcome-category-filter" value="${category}" checked style="margin-right: 8px;">
                    <span class="${colorClass}" style="font-size: 0.9rem;">${category}</span>
                  </label>
                `;
                }).join('')}
              </div>
            </div>
            
            <!-- Success Probability Filter -->
            <div>
              <label style="display: block; font-weight: 500; margin-bottom: 8px; font-size: 0.9rem;">
                Minimum Success Probability: <span id="minProbValue">0</span>%
              </label>
              <input type="range" id="minSuccessProbFilter" min="0" max="100" step="5" value="0" 
                     style="width: 100%;" oninput="document.getElementById('minProbValue').textContent = this.value">
            </div>
            
            <button onclick="applyOutcomeFilters()" class="btn-primary" style="width: 100%; margin-top: 15px; padding: 10px;">
              Apply Filters
            </button>
            <button onclick="clearOutcomeFilters()" class="btn-secondary" style="width: 100%; margin-top: 8px; padding: 8px;">
              Clear Filters
            </button>
          </div>
          
          <!-- Sort Controls -->
          <div class="sort-panel" style="background: #f7fafc; padding: 20px; border-radius: 8px; border: 2px solid #e2e8f0;">
            <h5 style="margin-bottom: 15px; font-weight: 600;">Sort Patients</h5>
            
            <div style="margin-bottom: 15px;">
              <label style="display: block; font-weight: 500; margin-bottom: 8px; font-size: 0.9rem;">
                Sort by:
              </label>
              <select id="outcomeSortBy" style="width: 100%; padding: 8px; border: 2px solid #e2e8f0; border-radius: 6px; font-size: 0.9rem;">
                <option value="successProbability">Success Probability</option>
                <option value="category">Outcome Category</option>
                <option value="surgeryRisk">Surgery Risk</option>
                <option value="patientId">Patient ID</option>
              </select>
            </div>
            
            <div>
              <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                <input type="radio" name="outcomeSortOrder" value="desc" checked style="margin-right: 4px;">
                <span style="font-size: 0.9rem;">Descending (High to Low)</span>
              </label>
              <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; margin-top: 8px;">
                <input type="radio" name="outcomeSortOrder" value="asc" style="margin-right: 4px;">
                <span style="font-size: 0.9rem;">Ascending (Low to High)</span>
              </label>
            </div>
            
            <button onclick="applyOutcomeSort()" class="btn-primary" style="width: 100%; margin-top: 15px; padding: 10px;">
              Apply Sort
            </button>
          </div>
        </div>
        
        <!-- Patient List Display -->
        <div id="filteredPatientList" style="margin-top: 20px;">
          <h4>Patient Outcomes</h4>
          <div id="patientOutcomesContainer" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; margin-top: 15px;">
            <!-- Populated by JavaScript -->
          </div>
          <div id="filteredCount" style="margin-top: 15px; padding: 10px; background: #e2e8f0; border-radius: 6px; text-align: center;">
            <strong>Showing <span id="filteredCountValue">0</span> of <span id="totalCountValue">0</span> patients</strong>
          </div>
        </div>
      </div>
      
      <div class="download-section">
        <h4>Download Outcome Predictions</h4>
        <button class="btn-primary" onclick="downloadOutcomes()">
          Download CSV (Surgery Risk + Success Probability)
        </button>
        </div>
      `;
  }
  
  // Add success category legend for single patient too
  html += `
      <div class="success-category-legend" style="margin-top: 30px;">
        <h4>Outcome Categories</h4>
        <p class="legend-note">
          <strong>Success Definition:</strong> A successful outcome is defined as ≥30 points improvement in symptoms and function.
          Categories are based on validated clinical outcome measures.
        </p>
        <p class="legend-note" style="margin-top: 8px; font-size: 0.9em; color: #666;">
          <strong>Note:</strong> These predictions are based on OAI data and should be validated 
          against Bergman Clinics' surgical outcomes before clinical use.
        </p>
      </div>
    </div>
  `;

  resultsDiv.innerHTML = html;
  resultsDiv.style.display = "block";

  // Store CSV for download
  window.outcomeCSV = outcomes.csv;
  
  // Store patient outcomes data for filtering/sorting
  window.patientOutcomesData = outcomes.patient_outcomes || [];
  
  // Only show filtering/sorting and charts for multiple patients
  if (!isSinglePatient) {
  // Initial display of all patients
  displayFilteredPatients(window.patientOutcomesData);

  // Render success category distribution chart
  if (outcomes.success_plot || outcomes.improvement_plot) {
    setTimeout(() => {
      const plotData = outcomes.success_plot || outcomes.improvement_plot;
      renderImprovementChart(plotData);
    }, 100);
    }
  }

  // Scroll to results
  resultsDiv.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderImprovementChart(plotData) {
  const ctx = document.getElementById("improvementChart");
  if (!ctx || !plotData || !plotData.data) return;

  // Map labels to colors based on success categories
  const getColorForLabel = (label) => {
    if (label.includes("Excellent")) return "#10b981"; // green-500
    if (label.includes("Successful")) return "#3b82f6"; // blue-500
    if (label.includes("Moderate")) return "#eab308"; // yellow-500
    if (label.includes("Limited")) return "#f97316"; // orange-500
    if (label.includes("Minimal")) return "#ef4444"; // red-500
    // Fallback for old labels
    if (label.includes("Excellent") || label.includes(">30")) return "#10b981";
    if (label.includes("Good") || label.includes("20-30")) return "#22c55e";
    if (label.includes("Moderate") || label.includes("10-20")) return "#eab308";
    if (label.includes("Minimal") || label.includes("0-10")) return "#f97316";
    return "#6b7280"; // gray-500
  };

  const colors = plotData.data.labels.map(getColorForLabel);

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: plotData.data.labels,
      datasets: [
        {
          label: plotData.ylabel,
          data: plotData.data.values,
          backgroundColor: colors,
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
  a.download = "DOC_Surgical_Outcomes_Report.csv";
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

// CSV upload functions removed - manual entry only

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
  const checkedRadio = document.querySelector('input[name="painScoreType"]:checked');
  if (!checkedRadio) {
    console.warn("No pain score type radio button selected");
    return;
  }
  
  const painScoreType = checkedRadio.value;
  const womacRField = document.getElementById("womac_r_field");
  const womacLField = document.getElementById("womac_l_field");
  const vasRField = document.getElementById("vas_r_field");
  const vasLField = document.getElementById("vas_l_field");
  const vasInfo = document.getElementById("vasInfo");

  if (!womacRField || !womacLField || !vasRField || !vasLField) {
    console.warn("Pain score fields not found in DOM");
    return;
  }

  if (painScoreType === "vas") {
    // Show VAS fields, hide WOMAC fields
    womacRField.style.display = "none";
    womacLField.style.display = "none";
    vasRField.style.display = "block";
    vasLField.style.display = "block";
    vasInfo.style.display = "block";

    // Pain scores are optional - never required
    const vasRRest = document.getElementById("vas_r_rest");
    const vasRWalking = document.getElementById("vas_r_walking");
    const vasLRest = document.getElementById("vas_l_rest");
    const vasLWalking = document.getElementById("vas_l_walking");
    if (vasRRest) vasRRest.required = false;
    if (vasRWalking) vasRWalking.required = false;
    if (vasLRest) vasLRest.required = false;
    if (vasLWalking) vasLWalking.required = false;
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
    const vasRRest = document.getElementById("vas_r_rest");
    const vasRWalking = document.getElementById("vas_r_walking");
    const vasLRest = document.getElementById("vas_l_rest");
    const vasLWalking = document.getElementById("vas_l_walking");
    if (vasRRest) vasRRest.required = false;
    if (vasRWalking) vasRWalking.required = false;
    if (vasLRest) vasLRest.required = false;
    if (vasLWalking) vasLWalking.required = false;
    document.getElementById("womac_r").required = false;
    document.getElementById("womac_l").required = false;

    // Clear all fields
    document.getElementById("womac_r").value = "";
    document.getElementById("womac_l").value = "";
    const vasRRest2 = document.getElementById("vas_r_rest");
    const vasRWalking2 = document.getElementById("vas_r_walking");
    const vasLRest2 = document.getElementById("vas_l_rest");
    const vasLWalking2 = document.getElementById("vas_l_walking");
    if (vasRRest2) vasRRest2.value = "";
    if (vasRWalking2) vasRWalking2.value = "";
    if (vasLRest2) vasLRest2.value = "";
    if (vasLWalking2) vasLWalking2.value = "";
    const vasRWomac2 = document.getElementById("vas_r_womac");
    const vasLWomac2 = document.getElementById("vas_l_womac");
    if (vasRWomac2) vasRWomac2.textContent = "--";
    if (vasLWomac2) vasLWomac2.textContent = "--";
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
    const vasRRest4 = document.getElementById("vas_r_rest");
    const vasRWalking4 = document.getElementById("vas_r_walking");
    const vasLRest4 = document.getElementById("vas_l_rest");
    const vasLWalking4 = document.getElementById("vas_l_walking");
    if (vasRRest4) vasRRest4.required = false;
    if (vasRWalking4) vasRWalking4.required = false;
    if (vasLRest4) vasLRest4.required = false;
    if (vasLWalking4) vasLWalking4.required = false;

    // Clear VAS fields
    const vasRRest3 = document.getElementById("vas_r_rest");
    const vasRWalking3 = document.getElementById("vas_r_walking");
    const vasLRest3 = document.getElementById("vas_l_rest");
    const vasLWalking3 = document.getElementById("vas_l_walking");
    if (vasRRest3) vasRRest3.value = "";
    if (vasRWalking3) vasRWalking3.value = "";
    if (vasLRest3) vasLRest3.value = "";
    if (vasLWalking3) vasLWalking3.value = "";
    const vasRWomac3 = document.getElementById("vas_r_womac");
    const vasLWomac3 = document.getElementById("vas_l_womac");
    if (vasRWomac3) vasRWomac3.textContent = "--";
    if (vasLWomac3) vasLWomac3.textContent = "--";
  }
}

// Real-time VAS to WOMAC conversion display - using average of rest and walking
function updateVasWomacDisplay(side) {
  const restField = document.getElementById(`vas_${side}_rest`);
  const walkingField = document.getElementById(`vas_${side}_walking`);
  const womacDisplay = document.getElementById(`vas_${side}_womac`);
  
  if (!restField || !walkingField || !womacDisplay) return;
  
  const restValue = parseFloat(restField.value);
  const walkingValue = parseFloat(walkingField.value);
  
  // Calculate average if at least one value is provided
  let avgVas = null;
  if (!isNaN(restValue) && restValue >= 0 && restValue <= 10 && 
      !isNaN(walkingValue) && walkingValue >= 0 && walkingValue <= 10) {
    // Both provided - use average
    avgVas = (restValue + walkingValue) / 2;
  } else if (!isNaN(restValue) && restValue >= 0 && restValue <= 10) {
    // Only rest provided
    avgVas = restValue;
  } else if (!isNaN(walkingValue) && walkingValue >= 0 && walkingValue <= 10) {
    // Only walking provided
    avgVas = walkingValue;
  }
  
  if (avgVas !== null) {
    const womacEstimate = vasToWomac(avgVas);
    womacDisplay.textContent = womacEstimate.toFixed(1);
  } else {
    womacDisplay.textContent = "--";
  }
}

// Attach event listeners to all VAS fields
document.getElementById("vas_r_rest")?.addEventListener("input", () => updateVasWomacDisplay("r"));
document.getElementById("vas_r_walking")?.addEventListener("input", () => updateVasWomacDisplay("r"));
document.getElementById("vas_l_rest")?.addEventListener("input", () => updateVasWomacDisplay("l"));
document.getElementById("vas_l_walking")?.addEventListener("input", () => updateVasWomacDisplay("l"));

// Form submission handler - analyze immediately
document.getElementById("patientForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const analyzeBtn = document.getElementById("analyzePatientBtn");
  const analyzeBtnText = document.getElementById("analyzeBtnText");
  const originalText = analyzeBtnText.textContent;
  
  // Disable button and show loading
  analyzeBtn.disabled = true;
  analyzeBtnText.textContent = "Analyzing...";
  analyzeBtn.style.opacity = "0.7";
  analyzeBtn.style.cursor = "not-allowed";

  // Show loading indicator (only if on step 1 or desktop)
  const loadingEl = document.getElementById("loading");
  const isMobileFormVisible = document.getElementById("mobilePatientForm") && 
                               window.getComputedStyle(document.getElementById("mobilePatientForm")).display !== "none";
  
  // Only show loading on step 1 or desktop
  if (!isMobileFormVisible || currentMobileStep === 1) {
    if (loadingEl) loadingEl.style.display = "flex";
  }
  const desktopResults = document.getElementById("results");
  if (desktopResults) desktopResults.style.display = "none";

  // Validate KL grades - at least one must be available (not "Not available")
  const kl_r_value = document.getElementById("kl_r").value;
  const kl_l_value = document.getElementById("kl_l").value;

  // Check if both are "Not available" or empty
  if (
    (kl_r_value === "" || kl_r_value === "na") &&
    (kl_l_value === "" || kl_l_value === "na")
  ) {
    document.getElementById("loading").style.display = "none";
    analyzeBtn.disabled = false;
    analyzeBtnText.textContent = originalText;
    analyzeBtn.style.opacity = "1";
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
      document.getElementById("loading").style.display = "none";
      analyzeBtn.disabled = false;
      analyzeBtnText.textContent = originalText;
      analyzeBtn.style.opacity = "1";
      alert("Invalid right knee KL grade. Please select a valid option.");
      return;
    }
  }

  if (kl_l_value !== "" && kl_l_value !== "na") {
    kl_l = parseInt(kl_l_value);
    if (isNaN(kl_l) || kl_l < 0 || kl_l > 4) {
      document.getElementById("loading").style.display = "none";
      analyzeBtn.disabled = false;
      analyzeBtnText.textContent = originalText;
      analyzeBtn.style.opacity = "1";
      alert("Invalid left knee KL grade. Please select a valid option.");
      return;
    }
  }

  // Check that at least one knee has OA findings (KL ≥ 1) if both are available
  if (kl_r !== null && kl_l !== null) {
    if (kl_r === 0 && kl_l === 0) {
      document.getElementById("loading").style.display = "none";
      analyzeBtn.disabled = false;
      analyzeBtnText.textContent = originalText;
      analyzeBtn.style.opacity = "1";
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
    // Convert VAS to WOMAC if provided - using average of rest and walking
    const vas_r_rest_str = document.getElementById("vas_r_rest")?.value.trim() || "";
    const vas_r_walking_str = document.getElementById("vas_r_walking")?.value.trim() || "";
    const vas_l_rest_str = document.getElementById("vas_l_rest")?.value.trim() || "";
    const vas_l_walking_str = document.getElementById("vas_l_walking")?.value.trim() || "";

    // Calculate average VAS for right knee
    if (vas_r_rest_str !== "" || vas_r_walking_str !== "") {
      let vas_r_rest = null;
      let vas_r_walking = null;
      
      if (vas_r_rest_str !== "") {
        vas_r_rest = parseFloat(vas_r_rest_str);
        if (isNaN(vas_r_rest) || vas_r_rest < 0 || vas_r_rest > 10) {
          alert("Please enter a valid VAS pain at rest score (0-10) for right knee, or leave empty.");
          return;
        }
      }
      
      if (vas_r_walking_str !== "") {
        vas_r_walking = parseFloat(vas_r_walking_str);
        if (isNaN(vas_r_walking) || vas_r_walking < 0 || vas_r_walking > 10) {
          alert("Please enter a valid VAS pain during walking score (0-10) for right knee, or leave empty.");
          return;
        }
      }
      
      // Calculate average (use single value if only one provided)
      let avg_vas_r = null;
      if (vas_r_rest !== null && vas_r_walking !== null) {
        avg_vas_r = (vas_r_rest + vas_r_walking) / 2;
      } else if (vas_r_rest !== null) {
        avg_vas_r = vas_r_rest;
      } else if (vas_r_walking !== null) {
        avg_vas_r = vas_r_walking;
      }
      
      if (avg_vas_r !== null) {
        womac_r = vasToWomac(avg_vas_r);
        vasUsed = true;
      }
    }

    // Calculate average VAS for left knee
    if (vas_l_rest_str !== "" || vas_l_walking_str !== "") {
      let vas_l_rest = null;
      let vas_l_walking = null;
      
      if (vas_l_rest_str !== "") {
        vas_l_rest = parseFloat(vas_l_rest_str);
        if (isNaN(vas_l_rest) || vas_l_rest < 0 || vas_l_rest > 10) {
          alert("Please enter a valid VAS pain at rest score (0-10) for left knee, or leave empty.");
          return;
        }
      }
      
      if (vas_l_walking_str !== "") {
        vas_l_walking = parseFloat(vas_l_walking_str);
        if (isNaN(vas_l_walking) || vas_l_walking < 0 || vas_l_walking > 10) {
          alert("Please enter a valid VAS pain during walking score (0-10) for left knee, or leave empty.");
          return;
        }
      }
      
      // Calculate average (use single value if only one provided)
      let avg_vas_l = null;
      if (vas_l_rest !== null && vas_l_walking !== null) {
        avg_vas_l = (vas_l_rest + vas_l_walking) / 2;
      } else if (vas_l_rest !== null) {
        avg_vas_l = vas_l_rest;
      } else if (vas_l_walking !== null) {
        avg_vas_l = vas_l_walking;
      }
      
      if (avg_vas_l !== null) {
        womac_l = vasToWomac(avg_vas_l);
        vasUsed = true;
      }
    }

    // Check if any VAS was provided
    if (!vasUsed) {
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
            "Please enter a valid symptom score (0-96) for right knee, or leave empty."
          );
          return;
        }
      }

      if (womac_l_str !== "") {
        womac_l = parseFloat(womac_l_str);
        if (isNaN(womac_l) || womac_l < 0 || womac_l > 96) {
          alert(
            "Please enter a valid symptom score (0-96) for left knee, or leave empty."
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

  // Walking distance (400m walk time) - optional
  const walkingDistanceStr = document.getElementById("walking_distance")?.value.trim() || "";
  const walking_distance = walkingDistanceStr !== "" ? parseFloat(walkingDistanceStr) : null;
  
  // Validate walking distance if provided
  if (walking_distance !== null) {
    if (isNaN(walking_distance) || walking_distance < 60 || walking_distance > 1200) {
      alert("Walking distance (400m walk time) must be between 60 and 1200 seconds (1-20 minutes), or leave empty.");
      return;
    }
  }

  // Previous TKA on other knee - optional, stored but not used in current model
  const previousTkaValue = document.getElementById("previous_tka_other_knee")?.value || "";
  const previous_tka_other_knee = previousTkaValue !== "" ? parseInt(previousTkaValue) : 0;

  const patient = {
    age: parseFloat(document.getElementById("age").value),
    sex: parseInt(document.getElementById("sex").value),
    bmi: parseFloat(document.getElementById("bmi").value),
    womac_r: womac_r, // Can be null
    womac_l: womac_l, // Can be null
    kl_r: kl_r, // Can be null if "Not available"
    kl_l: kl_l, // Can be null if "Not available"
    fam_hx: fam_hx,
    walking_distance: walking_distance, // Optional - 400m walk time in seconds
    previous_tka_other_knee: previous_tka_other_knee, // Stored for future use, not used in current model
    _pain_scores_missing: painScoresMissing, // Flag for display
    _kl_missing: kl_r === null || kl_l === null, // Flag for display
  };

  // Store VAS info for display if VAS was used (store both rest and walking separately)
  if (vasUsed) {
    patient._vas_used = true;
    const vas_r_rest_str = document.getElementById("vas_r_rest")?.value.trim() || "";
    const vas_r_walking_str = document.getElementById("vas_r_walking")?.value.trim() || "";
    const vas_l_rest_str = document.getElementById("vas_l_rest")?.value.trim() || "";
    const vas_l_walking_str = document.getElementById("vas_l_walking")?.value.trim() || "";
    
    patient._vas_r_rest = vas_r_rest_str !== "" ? parseFloat(vas_r_rest_str) : null;
    patient._vas_r_walking = vas_r_walking_str !== "" ? parseFloat(vas_r_walking_str) : null;
    patient._vas_l_rest = vas_l_rest_str !== "" ? parseFloat(vas_l_rest_str) : null;
    patient._vas_l_walking = vas_l_walking_str !== "" ? parseFloat(vas_l_walking_str) : null;
    
    // Also store averages for reference
    if (patient._vas_r_rest !== null && patient._vas_r_walking !== null) {
      patient._vas_r_avg = (patient._vas_r_rest + patient._vas_r_walking) / 2;
    } else if (patient._vas_r_rest !== null) {
      patient._vas_r_avg = patient._vas_r_rest;
    } else if (patient._vas_r_walking !== null) {
      patient._vas_r_avg = patient._vas_r_walking;
    }
    
    if (patient._vas_l_rest !== null && patient._vas_l_walking !== null) {
      patient._vas_l_avg = (patient._vas_l_rest + patient._vas_l_walking) / 2;
    } else if (patient._vas_l_rest !== null) {
      patient._vas_l_avg = patient._vas_l_rest;
    } else if (patient._vas_l_walking !== null) {
      patient._vas_l_avg = patient._vas_l_walking;
    }
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

  // Immediately analyze this single patient
  try {
    // Add minimum delay to show loading state (at least 800ms for UX)
    const startTime = Date.now();
    const minLoadingTime = 800;
    
    // Convert single patient to CSV format
    const csvHeaders = ["age", "sex", "bmi", "womac_r", "womac_l", "kl_r", "kl_l", "fam_hx", "walking_distance", "previous_tka_other_knee"];
    if (outcome !== "") {
      csvHeaders.push("tkr_outcome");
    }
    
    const csv = [
      csvHeaders.join(","),
      csvHeaders.map((h) => {
        const value = patient[h];
        if (value === null || value === undefined) {
          if (h === "kl_r" || h === "kl_l") {
            return "na";
          }
          return "";
        }
        return value;
      }).join(",")
    ].join("\n");
    
    const blob = new Blob([csv], { type: "text/csv" });
    const formData = new FormData();
    formData.append("file", blob, "patient.csv");
    formData.append("run_outcome", "true"); // Also run outcome prediction

    console.log("Analyzing patient...");
    const response = await fetch(`${API_BASE_URL}/api/validate`, {
      method: "POST",
      body: formData,
    });

    const responseText = await response.text();
    let data;

    try {
      data = JSON.parse(responseText);
    } catch (e) {
      throw new Error(`Server error: ${response.status} ${responseText.substring(0, 100)}`);
    }

    // Ensure minimum loading time for better UX
    const elapsed = Date.now() - startTime;
    const remainingTime = Math.max(0, minLoadingTime - elapsed);
    await new Promise(resolve => setTimeout(resolve, remainingTime));

    document.getElementById("loading").style.display = "none";
    analyzeBtn.disabled = false;
    analyzeBtnText.textContent = originalText;
    analyzeBtn.style.opacity = "1";

    if (data.error) {
      alert("Error: " + data.error);
      return;
    }

    console.log("Analysis complete, displaying results...");
    // Display results (outcomes are already included inline via displayResults)
    displayResults(data);
    
    // Scroll to results (check if mobile or desktop)
    const isMobileFormVisible = document.getElementById("mobilePatientForm") && 
                                 window.getComputedStyle(document.getElementById("mobilePatientForm")).display !== "none";
    if (isMobileFormVisible) {
      // Mobile: scroll to step 4
      const step4 = document.getElementById("mobileStep4");
      if (step4) step4.scrollIntoView({ behavior: "smooth", block: "start" });
    } else {
      // Desktop: scroll to desktop results
      const desktopResults = document.getElementById("results");
      if (desktopResults) desktopResults.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    
  } catch (error) {
    document.getElementById("loading").style.display = "none";
    analyzeBtn.disabled = false;
    analyzeBtnText.textContent = originalText;
    analyzeBtn.style.opacity = "1";
    alert("Error analyzing patient: " + error.message);
    console.error("Analysis error:", error);
  }
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
        // Display VAS info (rest and walking if available, otherwise average)
        let vasRDisplay = "N/A";
        let vasLDisplay = "N/A";
        if (p._vas_r_rest !== null && p._vas_r_walking !== null) {
          vasRDisplay = `Rest: ${p._vas_r_rest.toFixed(1)}, Walking: ${p._vas_r_walking.toFixed(1)}`;
        } else if (p._vas_r_avg !== null) {
          vasRDisplay = p._vas_r_avg.toFixed(1);
        }
        if (p._vas_l_rest !== null && p._vas_l_walking !== null) {
          vasLDisplay = `Rest: ${p._vas_l_rest.toFixed(1)}, Walking: ${p._vas_l_walking.toFixed(1)}`;
        } else if (p._vas_l_avg !== null) {
          vasLDisplay = p._vas_l_avg.toFixed(1);
        }
        painScoreNote = `<br><small style="color: #666;">Symptom scores estimated from VAS (R: ${vasRDisplay}, L: ${vasLDisplay})</small>`;
      } else if (p._pain_scores_missing) {
        painScoreNote = `<br><small style="color: #ff9800;">⚠️ No symptom assessment - reduced confidence</small>`;
      }

      const symptomDisplay =
        p.womac_r !== null && p.womac_l !== null
          ? `Symptoms: R=${p.womac_r.toFixed(1)}, L=${p.womac_l.toFixed(1)}`
          : p.womac_r !== null
          ? `Symptoms: R=${p.womac_r.toFixed(1)}, L=N/A`
          : p.womac_l !== null
          ? `Symptoms: R=N/A, L=${p.womac_l.toFixed(1)}`
          : `Symptoms: Not assessed`;

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
                ${symptomDisplay}${painScoreNote}
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

    const response = await fetch(`${API_BASE_URL}/api/validate`, {
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

// Initialize outcome prediction button handler
function attachOutcomeHandler() {
  const predictOutcomesBtn = document.getElementById("predictOutcomesBtn");
  if (predictOutcomesBtn) {
    // Remove any existing listeners by cloning the button
    const newBtn = predictOutcomesBtn.cloneNode(true);
    predictOutcomesBtn.parentNode.replaceChild(newBtn, predictOutcomesBtn);
    
    newBtn.addEventListener("click", function(e) {
      e.preventDefault();
      e.stopPropagation();
      console.log("Outcome prediction button clicked");
      predictOutcomes();
      return false;
    });
    console.log("✓ Outcome prediction handler attached");
  } else {
    // Retry if button not found yet (might be hidden initially)
    setTimeout(attachOutcomeHandler, 500);
  }
}

// ============================================================================
// Filter and Sort Functionality for Patient Outcomes
// ============================================================================

let currentFilteredPatients = [];

function displayFilteredPatients(patients) {
  const container = document.getElementById("patientOutcomesContainer");
  const filteredCountEl = document.getElementById("filteredCountValue");
  const totalCountEl = document.getElementById("totalCountValue");
  
  if (!container) return;
  
  currentFilteredPatients = patients;
  
  if (patients.length === 0) {
    container.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #666;">No patients match the current filters.</div>';
    if (filteredCountEl) filteredCountEl.textContent = "0";
    if (totalCountEl) totalCountEl.textContent = window.patientOutcomesData?.length || "0";
    return;
  }
  
  // Category color mapping (using actual hex colors)
  const categoryColors = {
    "Excellent Outcome": { bg: "#f0fdf4", text: "#15803d", border: "#bbf7d0" },
    "Successful Outcome": { bg: "#eff6ff", text: "#1d4ed8", border: "#bfdbfe" },
    "Moderate Improvement": { bg: "#fefce8", text: "#a16207", border: "#fef08a" },
    "Limited Improvement": { bg: "#fff7ed", text: "#c2410c", border: "#fed7aa" },
    "Minimal Improvement": { bg: "#fef2f2", text: "#dc2626", border: "#fecaca" },
  };
  
  container.innerHTML = patients.map((patient, index) => {
    const colors = categoryColors[patient.success_category] || { bg: "#f9fafb", text: "#374151", border: "#e5e7eb" };
    const patientId = patient.patient_id || `Patient ${patient.patient_number || index + 1}`;
    const sexDisplay = patient.sex === 1 ? "M" : patient.sex === 0 ? "F" : "N/A";
    
    return `
      <div class="patient-outcome-card" style="background: white; border: 2px solid ${colors.border}; border-radius: 8px; padding: 15px; transition: all 0.2s;">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
          <div>
            <h5 style="margin: 0; font-size: 1.1rem; color: #2d3748;">${patientId}</h5>
            <p style="margin: 4px 0 0 0; font-size: 0.85rem; color: #64748b;">
              Age ${patient.age || 'N/A'} • ${sexDisplay} • BMI ${patient.bmi ? patient.bmi.toFixed(1) : 'N/A'}
            </p>
          </div>
        </div>
        
        ${patient._womac_improvement !== undefined && patient._womac_improvement !== null ? `
          <div style="margin-bottom: 12px; padding: 12px; background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); border-radius: 8px; color: white;">
            <div style="font-size: 0.85rem; opacity: 0.9; margin-bottom: 4px;">Expected Improvement</div>
            <div style="font-size: 2rem; font-weight: 700; margin-bottom: 4px;">
              ${patient._womac_improvement.toFixed(1)} points
            </div>
            <div style="font-size: 0.8rem; opacity: 0.9;">
              ${patient._womac_improvement >= 30 
                ? `✓ Meets success threshold (≥30 points)` 
                : `Below threshold (needs ${(30 - patient._womac_improvement).toFixed(1)} more points)`}
            </div>
          </div>
        ` : ''}
        
        <div style="padding: 12px; background: ${colors.bg}; border-radius: 6px; border-left: 4px solid ${colors.border};">
          <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 4px;">Expected Outcome</div>
          <div style="font-size: 1.1rem; font-weight: 600; color: ${colors.text}; margin-bottom: 8px;">
            ${patient.success_category}
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.85rem; color: #64748b;">Success Probability</span>
            <span style="font-size: 1.4rem; font-weight: 700; color: ${colors.text};">
              ${patient.success_probability}%
            </span>
          </div>
          ${patient.category_description ? `
            <div style="font-size: 0.8rem; color: #64748b; margin-top: 8px; font-style: italic;">
              ${patient.category_description}
            </div>
          ` : ''}
        </div>
        
        ${patient.surgery_risk !== null && patient.risk_category ? `
          <div style="margin-top: 12px; padding: 8px; background: #f7fafc; border-radius: 6px;">
            <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 4px;">Surgery Risk</div>
            <div style="font-size: 1.3rem; font-weight: 600; color: #2d3748;">${patient.surgery_risk.toFixed(1)}%</div>
            <div style="font-size: 0.8rem; color: #64748b;">${patient.risk_category}</div>
          </div>
        ` : ''}
      </div>
    `;
  }).join('');
  
  if (filteredCountEl) filteredCountEl.textContent = patients.length;
  if (totalCountEl) totalCountEl.textContent = window.patientOutcomesData?.length || "0";
}

function applyOutcomeFilters() {
  if (!window.patientOutcomesData || window.patientOutcomesData.length === 0) {
    alert("No patient outcome data available");
    return;
  }
  
  // Get selected categories
  const categoryCheckboxes = document.querySelectorAll('.outcome-category-filter:checked');
  const selectedCategories = Array.from(categoryCheckboxes).map(cb => cb.value);
  
  // Get minimum probability
  const minProbInput = document.getElementById('minSuccessProbFilter');
  const minProbability = minProbInput ? parseInt(minProbInput.value) : 0;
  
  // Filter patients
  let filtered = window.patientOutcomesData.filter(patient => {
    // Category filter
    if (selectedCategories.length > 0 && !selectedCategories.includes(patient.success_category)) {
      return false;
    }
    
    // Probability filter
    if (patient.success_probability < minProbability) {
      return false;
    }
    
    return true;
  });
  
  // Apply current sort
  applyOutcomeSort(filtered);
}

function applyOutcomeSort(preFiltered = null) {
  const patients = preFiltered || currentFilteredPatients || window.patientOutcomesData || [];
  
  const sortBySelect = document.getElementById('outcomeSortBy');
  const sortOrderRadios = document.querySelectorAll('input[name="outcomeSortOrder"]:checked');
  
  if (!sortBySelect) {
    displayFilteredPatients(patients);
    return;
  }
  
  const sortBy = sortBySelect.value;
  const sortOrder = sortOrderRadios.length > 0 ? sortOrderRadios[0].value : 'desc';
  
  // Category order for sorting
  const categoryOrder = {
    "Excellent Outcome": 5,
    "Successful Outcome": 4,
    "Moderate Improvement": 3,
    "Limited Improvement": 2,
    "Minimal Improvement": 1
  };
  
  const sorted = [...patients].sort((a, b) => {
    let comparison = 0;
    
    switch (sortBy) {
      case 'successProbability':
        comparison = (a.success_probability || 0) - (b.success_probability || 0);
        break;
      case 'category':
        comparison = (categoryOrder[a.success_category] || 0) - (categoryOrder[b.success_category] || 0);
        break;
      case 'surgeryRisk':
        comparison = (a.surgery_risk || 0) - (b.surgery_risk || 0);
        break;
      case 'patientId':
        const idA = a.patient_id || `Patient ${a.patient_number || 0}`;
        const idB = b.patient_id || `Patient ${b.patient_number || 0}`;
        comparison = idA.localeCompare(idB);
        break;
      default:
        comparison = 0;
    }
    
    return sortOrder === 'asc' ? comparison : -comparison;
  });
  
  currentFilteredPatients = sorted;
  displayFilteredPatients(sorted);
}

function clearOutcomeFilters() {
  // Check all category filters
  document.querySelectorAll('.outcome-category-filter').forEach(cb => {
    cb.checked = true;
  });
  
  // Reset probability filter
  const minProbInput = document.getElementById('minSuccessProbFilter');
  if (minProbInput) {
    minProbInput.value = 0;
    const minProbValue = document.getElementById('minProbValue');
    if (minProbValue) minProbValue.textContent = '0';
  }
  
  // Show all patients
  applyOutcomeFilters();
}

// Initialize outcome handler when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", attachOutcomeHandler);
} else {
  attachOutcomeHandler();
}

// ==================== MOBILE MULTI-STEP FORM ====================

let currentMobileStep = 1;
const totalMobileSteps = 4;

function mobileNextStep() {
  // Validate current step before proceeding
  if (currentMobileStep === 1) {
    // Validate Step 1: Basic Info
    const age = document.getElementById("mobile_age").value;
    const sex = document.getElementById("mobile_sex").value;
    const bmi = document.getElementById("mobile_bmi").value;
    
    if (!age || !sex || !bmi) {
      alert("Please fill in all required fields: Age, Sex, and BMI.");
      return;
    }
    
    // Sync to desktop form
    syncMobileToDesktop();
  } else if (currentMobileStep === 2) {
    // Step 2 validation is optional (pain scores)
    syncMobileToDesktop();
  }
  
  if (currentMobileStep < totalMobileSteps) {
    // Hide current step
    const currentStepEl = document.getElementById(`mobileStep${currentMobileStep}`);
    if (currentStepEl) {
      currentStepEl.classList.remove("active");
    }
    // Show next step
    currentMobileStep++;
    const nextStepEl = document.getElementById(`mobileStep${currentMobileStep}`);
    if (nextStepEl) {
      nextStepEl.classList.add("active");
    }
    // Update step indicators
    updateMobileStepIndicators();
    // Sync desktop to mobile for step 3
    if (currentMobileStep === 3) {
      syncDesktopToMobile();
    }
    // Update privacy notice visibility
    updateMobileStepVisibility();
    // Scroll to top
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
}

function mobilePrevStep() {
  if (currentMobileStep > 1) {
    // Hide current step
    const currentStepEl = document.getElementById(`mobileStep${currentMobileStep}`);
    if (currentStepEl) {
      currentStepEl.classList.remove("active");
    }
    // Show previous step
    currentMobileStep--;
    const prevStepEl = document.getElementById(`mobileStep${currentMobileStep}`);
    if (prevStepEl) {
      prevStepEl.classList.add("active");
    }
    // Update step indicators
    updateMobileStepIndicators();
    // Update privacy notice visibility
    updateMobileStepVisibility();
    // Scroll to top
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
}

function updateMobileStepVisibility() {
  // Toggle body class for CSS to hide privacy notice
  document.body.classList.remove("mobile-step-1", "mobile-step-2", "mobile-step-3", "mobile-step-4");
  document.body.classList.add(`mobile-step-${currentMobileStep}`);
  
  // Also directly toggle visibility
  const privacyNotice = document.querySelector(".privacy-notice.mobile-step-1-only");
  const introText = document.querySelectorAll(".mobile-step-1-only");
  const loadingEl = document.getElementById("loading");
  
  if (currentMobileStep === 1) {
    introText.forEach(el => {
      if (el && el !== loadingEl) el.style.display = "block";
    });
    // Loading should only show if it was explicitly set to show (during analysis)
    // Don't force it to show here
  } else {
    introText.forEach(el => {
      if (el) el.style.display = "none";
    });
    // Always hide loading on steps 2-4
    if (loadingEl) loadingEl.style.display = "none";
  }
}

function updateMobileStepIndicators() {
  const indicators = document.querySelectorAll(".step-dot");
  indicators.forEach((dot, index) => {
    if (index + 1 === currentMobileStep) {
      dot.classList.add("active");
    } else {
      dot.classList.remove("active");
    }
  });
}

function mobileTogglePainScoreType() {
  const painScoreType = document.querySelector('input[name="mobile_painScoreType"]:checked').value;
  
  // Show/hide fields based on selection
  const womacRField = document.getElementById("mobile_womac_r_field");
  const womacLField = document.getElementById("mobile_womac_l_field");
  const vasRField = document.getElementById("mobile_vas_r_field");
  const vasLField = document.getElementById("mobile_vas_l_field");
  
  if (painScoreType === "womac") {
    if (womacRField) womacRField.style.display = "block";
    if (womacLField) womacLField.style.display = "block";
    if (vasRField) vasRField.style.display = "none";
    if (vasLField) vasLField.style.display = "none";
  } else if (painScoreType === "vas") {
    if (womacRField) womacRField.style.display = "none";
    if (womacLField) womacLField.style.display = "none";
    if (vasRField) vasRField.style.display = "block";
    if (vasLField) vasLField.style.display = "block";
  } else {
    // "none"
    if (womacRField) womacRField.style.display = "none";
    if (womacLField) womacLField.style.display = "none";
    if (vasRField) vasRField.style.display = "none";
    if (vasLField) vasLField.style.display = "none";
  }
  
  // Update VAS WOMAC display if VAS is selected
  if (painScoreType === "vas") {
    updateMobileVasWomacDisplay();
  }
}

function updateMobileVasWomacDisplay() {
  const vas_r_rest = parseFloat(document.getElementById("mobile_vas_r_rest")?.value || 0);
  const vas_r_walking = parseFloat(document.getElementById("mobile_vas_r_walking")?.value || 0);
  const vas_l_rest = parseFloat(document.getElementById("mobile_vas_l_rest")?.value || 0);
  const vas_l_walking = parseFloat(document.getElementById("mobile_vas_l_walking")?.value || 0);
  
  // Calculate averages
  let avg_r = null;
  if (vas_r_rest > 0 || vas_r_walking > 0) {
    const count = (vas_r_rest > 0 ? 1 : 0) + (vas_r_walking > 0 ? 1 : 0);
    avg_r = ((vas_r_rest > 0 ? vas_r_rest : 0) + (vas_r_walking > 0 ? vas_r_walking : 0)) / count;
  }
  
  let avg_l = null;
  if (vas_l_rest > 0 || vas_l_walking > 0) {
    const count = (vas_l_rest > 0 ? 1 : 0) + (vas_l_walking > 0 ? 1 : 0);
    avg_l = ((vas_l_rest > 0 ? vas_l_rest : 0) + (vas_l_walking > 0 ? vas_l_walking : 0)) / count;
  }
  
  // Convert to WOMAC and display
  const womacRDisplay = document.getElementById("mobile_vas_r_womac");
  const womacLDisplay = document.getElementById("mobile_vas_l_womac");
  
  if (womacRDisplay && avg_r !== null) {
    womacRDisplay.textContent = vasToWomac(avg_r).toFixed(1);
  } else if (womacRDisplay) {
    womacRDisplay.textContent = "--";
  }
  
  if (womacLDisplay && avg_l !== null) {
    womacLDisplay.textContent = vasToWomac(avg_l).toFixed(1);
  } else if (womacLDisplay) {
    womacLDisplay.textContent = "--";
  }
}

// Add event listeners for VAS fields to update display
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", function() {
    const vasFields = ["mobile_vas_r_rest", "mobile_vas_r_walking", "mobile_vas_l_rest", "mobile_vas_l_walking"];
    vasFields.forEach(fieldId => {
      const field = document.getElementById(fieldId);
      if (field) {
        field.addEventListener("input", updateMobileVasWomacDisplay);
      }
    });
  });
} else {
  const vasFields = ["mobile_vas_r_rest", "mobile_vas_r_walking", "mobile_vas_l_rest", "mobile_vas_l_walking"];
  vasFields.forEach(fieldId => {
    const field = document.getElementById(fieldId);
    if (field) {
      field.addEventListener("input", updateMobileVasWomacDisplay);
    }
  });
}

function syncMobileToDesktop() {
  // Copy ALL values from mobile form to desktop form
  const fields = [
    { mobile: "mobile_patientId", desktop: "patientId" },
    { mobile: "mobile_age", desktop: "age" },
    { mobile: "mobile_sex", desktop: "sex" },
    { mobile: "mobile_bmi", desktop: "bmi" },
    { mobile: "mobile_womac_r", desktop: "womac_r" },
    { mobile: "mobile_womac_l", desktop: "womac_l" },
    { mobile: "mobile_vas_r_rest", desktop: "vas_r_rest" },
    { mobile: "mobile_vas_r_walking", desktop: "vas_r_walking" },
    { mobile: "mobile_vas_l_rest", desktop: "vas_l_rest" },
    { mobile: "mobile_vas_l_walking", desktop: "vas_l_walking" },
    { mobile: "mobile_kl_r", desktop: "kl_r" },
    { mobile: "mobile_kl_l", desktop: "kl_l" },
    { mobile: "mobile_fam_hx", desktop: "fam_hx" },
    { mobile: "mobile_walking_distance", desktop: "walking_distance" },
    { mobile: "mobile_previous_tka_other_knee", desktop: "previous_tka_other_knee" },
    { mobile: "mobile_tkr_outcome", desktop: "tkr_outcome" },
  ];
  
  fields.forEach(({ mobile, desktop }) => {
    const mobileField = document.getElementById(mobile);
    const desktopField = document.getElementById(desktop);
    if (mobileField && desktopField) {
      desktopField.value = mobileField.value;
    }
  });
  
  // Sync pain score type
  const mobilePainType = document.querySelector('input[name="mobile_painScoreType"]:checked');
  if (mobilePainType) {
    const desktopPainType = document.querySelector(`input[name="painScoreType"][value="${mobilePainType.value}"]`);
    if (desktopPainType) {
      desktopPainType.checked = true;
      togglePainScoreType();
    }
  }
}

function syncDesktopToMobile() {
  // Copy values from desktop form to mobile form (for step 3)
  const fields = [
    { desktop: "womac_r", mobile: "mobile_womac_r" },
    { desktop: "womac_l", mobile: "mobile_womac_l" },
    { desktop: "vas_r_rest", mobile: "mobile_vas_r_rest" },
    { desktop: "vas_r_walking", mobile: "mobile_vas_r_walking" },
    { desktop: "vas_l_rest", mobile: "mobile_vas_l_rest" },
    { desktop: "vas_l_walking", mobile: "mobile_vas_l_walking" },
    { desktop: "kl_r", mobile: "mobile_kl_r" },
    { desktop: "kl_l", mobile: "mobile_kl_l" },
    { desktop: "fam_hx", mobile: "mobile_fam_hx" },
    { desktop: "walking_distance", mobile: "mobile_walking_distance" },
    { desktop: "previous_tka_other_knee", mobile: "mobile_previous_tka_other_knee" },
    { desktop: "tkr_outcome", mobile: "mobile_tkr_outcome" },
  ];
  
  fields.forEach(({ desktop, mobile }) => {
    const desktopField = document.getElementById(desktop);
    const mobileField = document.getElementById(mobile);
    if (desktopField && mobileField) {
      mobileField.value = desktopField.value;
    }
  });
  
  // Sync pain score type and toggle
  const desktopPainType = document.querySelector('input[name="painScoreType"]:checked');
  if (desktopPainType) {
    const mobilePainType = document.querySelector(`input[name="mobile_painScoreType"][value="${desktopPainType.value}"]`);
    if (mobilePainType) {
      mobilePainType.checked = true;
      mobileTogglePainScoreType();
    }
  }
}

function mobileClearForm() {
  // Reset mobile form
  document.getElementById("mobilePatientForm").reset();
  
  // Reset to step 1 - hide all steps, show only step 1
  const step1 = document.getElementById("mobileStep1");
  const step2 = document.getElementById("mobileStep2");
  const step3 = document.getElementById("mobileStep3");
  const step4 = document.getElementById("mobileStep4");
  
  if (step1) step1.classList.remove("active");
  if (step2) step2.classList.remove("active");
  if (step3) step3.classList.remove("active");
  if (step4) step4.classList.remove("active");
  
  if (step1) step1.classList.add("active");
  
  // Clear mobile results
  const mobileResults = document.getElementById("mobileResults");
  if (mobileResults) mobileResults.innerHTML = "";
  
  currentMobileStep = 1;
  updateMobileStepIndicators();
  updateMobileStepVisibility();
  
  // Reset pain score type
  const womacRadio = document.querySelector('input[name="mobile_painScoreType"][value="womac"]');
  if (womacRadio) {
    womacRadio.checked = true;
    mobileTogglePainScoreType();
  }
  
  // Also clear desktop form
  clearForm();
  
  // Scroll to top
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// Mobile form submission handler
const mobileForm = document.getElementById("mobilePatientForm");
if (mobileForm) {
  mobileForm.addEventListener("submit", async function(e) {
    e.preventDefault();
    
    // Sync all mobile values to desktop form
    syncMobileToDesktop();
    
    // Create a synthetic submit event and trigger desktop form handler
    const desktopForm = document.getElementById("patientForm");
    if (desktopForm) {
      // Create and dispatch submit event
      const submitEvent = new Event("submit", { cancelable: true, bubbles: true });
      desktopForm.dispatchEvent(submitEvent);
    }
  });
}

// Initialize mobile form on load
function initializeMobileForm() {
  // Ensure only step 1 is visible initially
  const step1 = document.getElementById("mobileStep1");
  const step2 = document.getElementById("mobileStep2");
  const step3 = document.getElementById("mobileStep3");
  const step4 = document.getElementById("mobileStep4");
  
  // Remove active class from all steps
  if (step1) step1.classList.remove("active");
  if (step2) step2.classList.remove("active");
  if (step3) step3.classList.remove("active");
  if (step4) step4.classList.remove("active");
  
  // Add active class to step 1
  if (step1) step1.classList.add("active");
  
  currentMobileStep = 1;
  updateMobileStepIndicators();
  updateMobileStepVisibility();
  
  // Initialize pain score type
  const womacRadio = document.querySelector('input[name="mobile_painScoreType"][value="womac"]');
  if (womacRadio) {
    womacRadio.checked = true;
    mobileTogglePainScoreType();
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeMobileForm);
} else {
  initializeMobileForm();
}
