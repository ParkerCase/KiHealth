#!/usr/bin/env node

/**
 * LINCS Monitoring System
 *
 * Monitors LINCS L1000 database for drug-gene interactions
 * No API key required - uses public LINCS API
 *
 * Stores results in Xata 'lincs_data' table
 */

require("dotenv").config();
const axios = require("axios");
const { getXataClient } = require("./google-sheets-storage"); // Use Google Sheets (falls back to file storage)
const fs = require("fs");
const path = require("path");

// Configuration
const TARGET_GENES = [
  { symbol: "STK17A", entrezId: "9263" },
  { symbol: "MYLK4", entrezId: "340156" },
  { symbol: "TBK1", entrezId: "29110" },
  { symbol: "CLK4", entrezId: "57396" },
  { symbol: "STK17B", entrezId: "9262" },
];

const LINCS_BASE_URL = "http://api.lincscloud.org/a2";
const MAX_REQUESTS_PER_SECOND = 2;
const MAX_RETRIES = 3;

// Setup logging
const logDir = path.join(__dirname, "..", "logs");
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}
const logFile = path.join(
  logDir,
  `lincs-${new Date().toISOString().split("T")[0]}.log`
);

function log(message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}\n`;
  console.log(message);
  fs.appendFileSync(logFile, logMessage);
}

// Xata client is now imported from file-storage.js (file-based, no API key needed)

// Rate limiting helper
let lastRequestTime = 0;
async function rateLimit() {
  const now = Date.now();
  const timeSinceLastRequest = now - lastRequestTime;
  const minInterval = 1000 / MAX_REQUESTS_PER_SECOND;

  if (timeSinceLastRequest < minInterval) {
    await new Promise((resolve) =>
      setTimeout(resolve, minInterval - timeSinceLastRequest)
    );
  }
  lastRequestTime = Date.now();
}

// Search LINCS for gene signatures
async function searchLINCS(geneSymbol, entrezId, retries = MAX_RETRIES) {
  await rateLimit();

  try {
    // LINCS L1000 API endpoint for gene signatures
    // Using the public API without authentication
    const url = `${LINCS_BASE_URL}/genes?filter={"where":{"entrez_id":${entrezId}}}`;

    log(`Searching LINCS for ${geneSymbol} (Entrez ID: ${entrezId})`);
    const response = await axios.get(url, {
      timeout: 30000,
      headers: {
        Accept: "application/json",
      },
    });

    if (!response.data || response.data.length === 0) {
      log(`No LINCS data found for ${geneSymbol}`);
      return [];
    }

    log(`Found ${response.data.length} signatures for ${geneSymbol}`);
    return response.data;
  } catch (error) {
    if (retries > 0) {
      log(
        `Error searching LINCS for ${geneSymbol} (${retries} retries left): ${error.message}`
      );
      await new Promise((resolve) => setTimeout(resolve, 2000));
      return searchLINCS(geneSymbol, entrezId, retries - 1);
    }
    log(
      `Failed to search LINCS for ${geneSymbol} after ${MAX_RETRIES} retries: ${error.message}`
    );
    return [];
  }
}

// Get compound perturbation data
async function getCompoundData(signatureId, retries = MAX_RETRIES) {
  await rateLimit();

  try {
    const url = `${LINCS_BASE_URL}/sigs?filter={"where":{"sig_id":"${signatureId}"}}`;

    const response = await axios.get(url, {
      timeout: 30000,
      headers: {
        Accept: "application/json",
      },
    });

    if (!response.data || response.data.length === 0) {
      return null;
    }

    return response.data[0];
  } catch (error) {
    if (retries > 0) {
      await new Promise((resolve) => setTimeout(resolve, 2000));
      return getCompoundData(signatureId, retries - 1);
    }
    log(`Error fetching compound data for ${signatureId}: ${error.message}`);
    return null;
  }
}

// Process LINCS data into our format
function processLINCSData(lincsData, targetGene) {
  const records = [];

  for (const signature of lincsData) {
    try {
      // Extract relevant information
      const compoundName =
        signature.pert_iname || signature.pert_type || "Unknown";
      const cellLine = signature.cell_id || "Unknown";
      const expressionChange = signature.score || 0;
      const mechanism = signature.pert_type || "Unknown";

      // Create unique ID
      const lincsId = `LINCS-${signature.sig_id || Date.now()}-${Math.random()
        .toString(36)
        .substr(2, 9)}`;

      // Calculate relevance score (simple heuristic)
      // Higher score if expression change is significant
      const relevanceScore = Math.abs(expressionChange) / 100; // Normalize to 0-1

      records.push({
        lincs_id: lincsId,
        compound_name: compoundName,
        target_gene: targetGene,
        cell_line: cellLine,
        efficacy_score: Math.abs(expressionChange),
        interaction_type: mechanism,
        data_source: "LINCS L1000",
        last_updated: new Date(),
      });
    } catch (error) {
      log(`Error processing LINCS signature: ${error.message}`);
    }
  }

  return records;
}

// Store records in Xata
async function storeLINCSRecords(xata, records) {
  let newCount = 0;
  let updatedCount = 0;
  let errorCount = 0;

  for (const record of records) {
    try {
      // Check if record already exists
      const existing = await xata.db.lincs_data
        .filter({ lincs_id: record.lincs_id })
        .getFirst();

      if (existing) {
        // Update existing record
        await xata.db.lincs_data.update(existing.id, {
          compound_name: record.compound_name,
          target_gene: record.target_gene,
          cell_line: record.cell_line,
          efficacy_score: record.efficacy_score,
          interaction_type: record.interaction_type,
          data_source: record.data_source,
          last_updated: new Date(),
        });
        updatedCount++;
      } else {
        // Create new record
        await xata.db.lincs_data.create(record);
        newCount++;
      }
    } catch (error) {
      log(`Error storing LINCS record ${record.lincs_id}: ${error.message}`);
      errorCount++;
    }
  }

  return { newCount, updatedCount, errorCount };
}

// Main execution
async function main() {
  log("=".repeat(80));
  log("LINCS Monitoring System - Starting");
  log("=".repeat(80));

  try {
    // Initialize file storage (replaces Xata)
    const xata = getXataClient();
    log("✓ Connected to file storage");

    const allRecords = [];

    // Search for each target gene
    for (const gene of TARGET_GENES) {
      log(`\nProcessing ${gene.symbol}...`);

      try {
        const lincsData = await searchLINCS(gene.symbol, gene.entrezId);

        if (lincsData.length > 0) {
          const processed = processLINCSData(lincsData, gene.symbol);
          allRecords.push(...processed);
          log(`  ✓ Processed ${processed.length} records for ${gene.symbol}`);
        }

        // Small delay between genes
        await new Promise((resolve) => setTimeout(resolve, 1000));
      } catch (error) {
        log(`Error processing ${gene.symbol}: ${error.message}`);
        // Continue with next gene
      }
    }

    log(`\nTotal records to store: ${allRecords.length}`);

    // Store in Xata
    if (allRecords.length > 0) {
      log("\nStoring records in file storage...");
      const results = await storeLINCSRecords(xata, allRecords);
      log(`✓ New records: ${results.newCount}`);
      log(`✓ Updated records: ${results.updatedCount}`);
      log(`✓ Errors: ${results.errorCount}`);
    } else {
      log("\nNo new records to store");
    }

    log("\n" + "=".repeat(80));
    log("LINCS Monitoring System - Complete");
    log("=".repeat(80));
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

module.exports = { main, searchLINCS, processLINCSData, storeLINCSRecords };
