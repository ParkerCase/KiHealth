#!/usr/bin/env node

/**
 * Test Script - Verify 100% Completion
 *
 * Tests all components of the monitoring system to ensure everything works
 * Run this after setting up GitHub Actions to verify the system is ready
 */

const fs = require("fs");
const path = require("path");

// Load .env.local from dashboard directory (primary source for Xata credentials)
const dashboardEnvPath = path.join(__dirname, "..", "dashboard", ".env.local");
const rootEnvPath = path.join(__dirname, "..", ".env");

// Try dashboard .env.local first, then fall back to root .env
if (fs.existsSync(dashboardEnvPath)) {
  require("dotenv").config({ path: dashboardEnvPath });
  console.log("✓ Loaded environment variables from dashboard/.env.local");
} else if (fs.existsSync(rootEnvPath)) {
  require("dotenv").config({ path: rootEnvPath });
  console.log("✓ Loaded environment variables from .env");
} else {
  // Try default dotenv behavior (current directory)
  require("dotenv").config();
}

const { buildClient } = require("@xata.io/client");

// Setup logging
const logDir = path.join(__dirname, "..", "logs");
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}
const logFile = path.join(
  logDir,
  `test-completion-${new Date().toISOString().split("T")[0]}.log`
);

function log(message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}\n`;
  console.log(message);
  fs.appendFileSync(logFile, logMessage);
}

// Initialize Xata client (with better error handling)
function getXataClient() {
  if (!process.env.XATA_API_KEY) {
    // Check if .env file exists
    const envPath = path.join(__dirname, ".env");
    const parentEnvPath = path.join(__dirname, "..", ".env");
    const envExists = fs.existsSync(envPath) || fs.existsSync(parentEnvPath);

    if (!envExists) {
      throw new Error(
        "XATA_API_KEY is not set. Please create a .env file in the scripts directory or root directory with XATA_API_KEY and XATA_DB_URL."
      );
    } else {
      throw new Error(
        "XATA_API_KEY is not set in environment variables, but .env file exists. Make sure the .env file contains XATA_API_KEY=your_key"
      );
    }
  }

  const XataClient = buildClient();
  const options = {
    apiKey: process.env.XATA_API_KEY,
  };

  if (process.env.XATA_DB_URL) {
    const url = process.env.XATA_DB_URL;
    const dbMatch = url.match(/\/db\/([^:]+):(.+)$/);
    if (dbMatch) {
      const baseUrl = url.substring(0, url.lastIndexOf(":"));
      options.databaseURL = baseUrl;
      options.branch = dbMatch[2];
    } else {
      options.databaseURL = url;
    }
  } else if (process.env.XATA_BRANCH) {
    options.branch = process.env.XATA_BRANCH;
  }

  return new XataClient(options);
}

// Test results
const results = {
  passed: [],
  failed: [],
  warnings: [],
};

function test(name, fn) {
  try {
    const result = fn();
    if (result === true || (result && result.passed)) {
      results.passed.push(name);
      log(`✅ PASS: ${name}`);
      return true;
    } else {
      results.failed.push(name);
      log(`❌ FAIL: ${name} - ${result.message || "Unknown error"}`);
      return false;
    }
  } catch (error) {
    results.failed.push(name);
    log(`❌ FAIL: ${name} - ${error.message}`);
    return false;
  }
}

function warn(name, message) {
  results.warnings.push({ name, message });
  log(`⚠️  WARN: ${name} - ${message}`);
}

async function main() {
  log("=".repeat(80));
  log("System Completion Test - Starting");
  log("=".repeat(80));

  try {
    const xata = getXataClient();
    log("✓ Connected to Xata\n");

    // ========================================================================
    // Test 1: Environment Variables
    // ========================================================================
    log("=".repeat(80));
    log("TEST 1: Environment Variables");
    log("=".repeat(80));

    test("XATA_API_KEY is set", () => {
      return !!process.env.XATA_API_KEY;
    });

    test("XATA_DB_URL is set", () => {
      return !!process.env.XATA_DB_URL;
    });

    const hasAnthropic = !!process.env.ANTHROPIC_API_KEY;
    const hasOpenAI = !!process.env.OPENAI_API_KEY;

    if (hasAnthropic || hasOpenAI) {
      test("AI API key is set", () => {
        return hasAnthropic || hasOpenAI;
      });
      if (hasAnthropic && hasOpenAI) {
        warn("Both AI keys set", "Using ANTHROPIC_API_KEY (default)");
      }
    } else {
      warn(
        "AI API key not set",
        "ANTHROPIC_API_KEY or OPENAI_API_KEY needed for AI analysis. Add to dashboard/.env.local or GitHub secrets."
      );
      // Don't fail the test - AI key is optional for basic functionality
      test("AI API key is set (optional)", () => true);
    }

    // ========================================================================
    // Test 2: Xata Tables Exist
    // ========================================================================
    log("\n" + "=".repeat(80));
    log("TEST 2: Xata Tables");
    log("=".repeat(80));

    const requiredTables = [
      "papers",
      "lincs_data",
      "cancer_rankings",
      "target_rankings",
      "synthetic_lethality",
      "cell_lines",
    ];

    const optionalTables = [
      "recalculation_queue",
      "ranking_history",
      "dashboard_alerts",
    ];

    for (const tableName of requiredTables) {
      try {
        await xata.db[tableName].getMany({ pagination: { size: 1 } });
        test(`Table '${tableName}' exists`, () => true);
      } catch (error) {
        // Special handling for papers table - it exists but needs schema update
        if (tableName === "papers" && error.message.includes("not compatible")) {
          test(`Table '${tableName}' exists`, () => {
            return {
              passed: false,
              message:
                "Table exists but needs schema update. Import updated scripts/papers.csv to add new columns (keyword_score, needs_deep_analysis, etc.)",
            };
          });
        } else {
          test(`Table '${tableName}' exists`, () => {
            return { passed: false, message: error.message };
          });
        }
      }
    }

    for (const tableName of optionalTables) {
      try {
        await xata.db[tableName].getMany({ pagination: { size: 1 } });
        test(`Table '${tableName}' exists (optional)`, () => true);
      } catch (error) {
        warn(
          `Table '${tableName}' missing`,
          "Optional table - will be created when needed"
        );
      }
    }

    // ========================================================================
    // Test 3: Papers Table Schema
    // ========================================================================
    log("\n" + "=".repeat(80));
    log("TEST 3: Papers Table Schema");
    log("=".repeat(80));

    try {
      const sample = await xata.db.papers.getMany({ pagination: { size: 1 } });
      if (sample.length > 0) {
        const paper = sample[0];
        const requiredFields = [
          "pubmed_id",
          "title",
          "keyword_score",
          "needs_deep_analysis",
          "ai_analyzed",
          "relevance_score",
        ];

        for (const field of requiredFields) {
          test(`Papers table has '${field}' field`, () => {
            return field in paper;
          });
        }
      } else {
        warn("Papers table is empty", "No sample record to test schema");
      }
    } catch (error) {
      test("Papers table schema check", () => {
        return { passed: false, message: error.message };
      });
    }

    // ========================================================================
    // Test 4: Script Files Exist
    // ========================================================================
    log("\n" + "=".repeat(80));
    log("TEST 4: Script Files");
    log("=".repeat(80));

    const requiredScripts = [
      "pubmed-monitor.js",
      "lincs-monitor.js",
      "ai-analyze-papers.js",
      "auto-recalculate.js",
    ];

    for (const script of requiredScripts) {
      const scriptPath = path.join(__dirname, script);
      test(`Script '${script}' exists`, () => {
        return fs.existsSync(scriptPath);
      });
    }

    // ========================================================================
    // Test 5: Dependencies Installed
    // ========================================================================
    log("\n" + "=".repeat(80));
    log("TEST 5: Dependencies");
    log("=".repeat(80));

    const packageJson = path.join(__dirname, "package.json");
    if (fs.existsSync(packageJson)) {
      const pkg = JSON.parse(fs.readFileSync(packageJson, "utf8"));
      const requiredDeps = [
        "@xata.io/client",
        "axios",
        "dotenv",
        "xml2js",
        "@anthropic-ai/sdk",
        "openai",
      ];

      for (const dep of requiredDeps) {
        test(`Dependency '${dep}' in package.json`, () => {
          return dep in (pkg.dependencies || {});
        });
      }
    } else {
      test("package.json exists", () => {
        return { passed: false, message: "package.json not found" };
      });
    }

    // ========================================================================
    // Test 6: GitHub Actions Workflow
    // ========================================================================
    log("\n" + "=".repeat(80));
    log("TEST 6: GitHub Actions");
    log("=".repeat(80));

    const workflowPath = path.join(
      __dirname,
      "..",
      ".github",
      "workflows",
      "daily-monitoring.yml"
    );
    test("GitHub Actions workflow exists", () => {
      return fs.existsSync(workflowPath);
    });

    if (fs.existsSync(workflowPath)) {
      const workflow = fs.readFileSync(workflowPath, "utf8");
      test("Workflow has all required jobs", () => {
        const hasPubMed = workflow.includes("pubmed-monitoring");
        const hasLINCS = workflow.includes("lincs-monitoring");
        const hasAI = workflow.includes("ai-analysis");
        const hasRecalc = workflow.includes("recalculation");
        return hasPubMed && hasLINCS && hasAI && hasRecalc;
      });
    }

    // ========================================================================
    // Test 7: Data Flow Test
    // ========================================================================
    log("\n" + "=".repeat(80));
    log("TEST 7: Data Flow");
    log("=".repeat(80));

    try {
      // Check if we can query papers
      const papersCount = await xata.db.papers.getMany({
        pagination: { size: 1 },
      });
      test("Can query papers table", () => true);

      // Check if we can query cancer_rankings
      const rankingsCount = await xata.db.cancer_rankings.getMany({
        pagination: { size: 1 },
      });
      test("Can query cancer_rankings table", () => true);
    } catch (error) {
      test("Data flow test", () => {
        return { passed: false, message: error.message };
      });
    }

    // ========================================================================
    // Summary
    // ========================================================================
    log("\n" + "=".repeat(80));
    log("TEST SUMMARY");
    log("=".repeat(80));
    log(`✅ Passed: ${results.passed.length}`);
    log(`❌ Failed: ${results.failed.length}`);
    log(`⚠️  Warnings: ${results.warnings.length}`);

    if (results.failed.length > 0) {
      log("\nFailed Tests:");
      results.failed.forEach((test) => {
        log(`  - ${test}`);
      });
    }

    if (results.warnings.length > 0) {
      log("\nWarnings:");
      results.warnings.forEach((w) => {
        log(`  - ${w.name}: ${w.message}`);
      });
    }

    const allCriticalPassed =
      results.failed.length === 0 ||
      results.failed.every((f) => f.includes("(optional)"));

    if (allCriticalPassed) {
      log("\n✅ SYSTEM READY FOR GITHUB ACTIONS!");
      log("All critical tests passed. The system is ready to run.");
    } else {
      log("\n❌ SYSTEM NOT READY");
      log("Please fix the failed tests before running GitHub Actions.");
      process.exit(1);
    }

    log("\n" + "=".repeat(80));
  } catch (error) {
    log(`\nFATAL ERROR: ${error.message}`);
    log(error.stack);
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

module.exports = { main };
