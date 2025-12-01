// DOC Risk Calculator - JavaScript

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("riskForm");
  const calculateBtn = document.getElementById("calculateBtn");
  const resetBtn = document.getElementById("resetBtn");
  const resultsDiv = document.getElementById("results");
  const errorDiv = document.getElementById("error");
  const printBtn = document.getElementById("printBtn");
  const newCalcBtn = document.getElementById("newCalcBtn");

  // Form submission
  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    // Hide previous results/errors
    resultsDiv.style.display = "none";
    errorDiv.style.display = "none";

    // Disable button
    calculateBtn.disabled = true;
    calculateBtn.textContent = "Calculating...";

    // Collect form data
    const formData = {
      age: document.getElementById("age").value,
      sex: document.getElementById("sex").value,
      bmi: document.getElementById("bmi").value,
      womac_right: document.getElementById("womac_right").value,
      womac_left: document.getElementById("womac_left").value,
      kl_right: document.getElementById("kl_right").value,
      kl_left: document.getElementById("kl_left").value,
      family_history: document.getElementById("family_history").value,
    };

    try {
      // Send request to backend
      const response = await fetch("/calculate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (data.error) {
        // Show error
        errorDiv.textContent = data.error;
        errorDiv.style.display = "block";
      } else if (data.success) {
        // Display results
        displayResults(data);
        resultsDiv.style.display = "block";

        // Scroll to results
        resultsDiv.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    } catch (error) {
      errorDiv.textContent = "An error occurred. Please try again.";
      errorDiv.style.display = "block";
      console.error("Error:", error);
    } finally {
      // Re-enable button
      calculateBtn.disabled = false;
      calculateBtn.textContent = "Calculate Risk";
    }
  });

  // Reset form
  resetBtn.addEventListener("click", function () {
    resultsDiv.style.display = "none";
    errorDiv.style.display = "none";
  });

  // Print results
  printBtn.addEventListener("click", function () {
    window.print();
  });

  // New calculation
  newCalcBtn.addEventListener("click", function () {
    form.reset();
    resultsDiv.style.display = "none";
    errorDiv.style.display = "none";
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  // Display results
  function displayResults(data) {
    const riskPercent = data.risk_percent;
    const category = data.category;
    const color = data.color;
    const interpretation = data.interpretation;

    // Update gauge
    updateGauge(riskPercent, color);

    // Update risk category
    const categoryValue = document.getElementById("categoryValue");
    categoryValue.textContent = category;
    categoryValue.style.backgroundColor = color;

    // Update percentage
    document.getElementById("percentageValue").textContent =
      riskPercent.toFixed(1) + "%";

    // Update interpretation
    document.getElementById("interpretationText").textContent = interpretation;
  }

  // Update gauge visualization
  function updateGauge(percent, color) {
    const gaugeFill = document.getElementById("gaugeFill");
    const gaugeValue = document.getElementById("gaugeValue");

    // Calculate stroke-dashoffset (565.48 is circumference of circle with r=90)
    // We want to fill from 0% to percent%
    const circumference = 565.48;
    const offset = circumference - (circumference * percent) / 100;

    // Update gauge
    gaugeFill.style.strokeDashoffset = offset;
    gaugeFill.style.stroke = color;

    // Update value text
    gaugeValue.textContent = percent.toFixed(1) + "%";
  }

  // Input validation
  const numberInputs = document.querySelectorAll('input[type="number"]');
  numberInputs.forEach((input) => {
    input.addEventListener("input", function () {
      const value = parseFloat(this.value);
      const min = parseFloat(this.min);
      const max = parseFloat(this.max);

      if (value < min) {
        this.value = min;
      } else if (value > max) {
        this.value = max;
      }
    });
  });
});
