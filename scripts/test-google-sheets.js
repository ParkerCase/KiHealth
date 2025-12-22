#!/usr/bin/env node
/**
 * Test Google Sheets Connection
 * Verifies that credentials work and can read/write to sheets
 */

require("dotenv").config({ path: "../.env.local" });
require("dotenv").config({ path: "../dashboard/.env.local" });

const { getXataClient } = require("./google-sheets-storage");

async function testConnection() {
  console.log("=".repeat(80));
  console.log("GOOGLE SHEETS CONNECTION TEST");
  console.log("=".repeat(80));

  // Check environment variables
  console.log("\n1. Checking Environment Variables...");
  const sheetId = process.env.GOOGLE_SHEET_ID;
  const serviceEmail = process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL;
  const privateKey = process.env.GOOGLE_PRIVATE_KEY;

  if (!sheetId) {
    console.log("   ❌ GOOGLE_SHEET_ID not found");
    console.log("   Expected: 1ejqaP2PVv1w1ygkLUocIPDnUrkWl9wtyzCoVrhuCxkQ");
    return false;
  } else {
    console.log(`   ✅ GOOGLE_SHEET_ID: ${sheetId.substring(0, 20)}...`);
  }

  if (!serviceEmail) {
    console.log("   ❌ GOOGLE_SERVICE_ACCOUNT_EMAIL not found");
    console.log("   Expected: monitoring-system@stroomtrition.iam.gserviceaccount.com");
    return false;
  } else {
    console.log(`   ✅ GOOGLE_SERVICE_ACCOUNT_EMAIL: ${serviceEmail}`);
  }

  if (!privateKey) {
    console.log("   ❌ GOOGLE_PRIVATE_KEY not found");
    return false;
  } else {
    console.log(`   ✅ GOOGLE_PRIVATE_KEY: Found (${privateKey.length} chars)`);
    if (privateKey.includes("\\n")) {
      console.log("   ⚠️  Warning: Private key contains \\n (should be actual newlines)");
    }
  }

  // Test connection
  console.log("\n2. Testing Google Sheets Connection...");
  try {
    const xata = getXataClient();
    console.log("   ✅ Xata client created");

    // Test creating a record
    console.log("\n3. Testing Write Operation...");
    const testRecord = {
      id: "test-" + Date.now(),
      title: "Connection Test",
      abstract: "This is a test to verify Google Sheets connection",
      test: true,
      timestamp: new Date().toISOString(),
    };

    const created = await xata.db.papers.create(testRecord);
    if (created && created.id) {
      console.log(`   ✅ Successfully created test record: ${created.id}`);
    } else {
      console.log("   ❌ Failed to create record");
      return false;
    }

    // Test reading the record
    console.log("\n4. Testing Read Operation...");
    const retrieved = await xata.db.papers.get(testRecord.id);
    if (retrieved && retrieved.title === "Connection Test") {
      console.log(`   ✅ Successfully retrieved test record`);
      console.log(`   ✅ Title: ${retrieved.title}`);
    } else {
      console.log("   ❌ Failed to retrieve record");
      return false;
    }

    // Test updating the record
    console.log("\n5. Testing Update Operation...");
    const updated = await xata.db.papers.update(testRecord.id, {
      title: "Connection Test - Updated",
    });
    if (updated && updated.title === "Connection Test - Updated") {
      console.log(`   ✅ Successfully updated test record`);
    } else {
      console.log("   ❌ Failed to update record");
      return false;
    }

    console.log("\n" + "=".repeat(80));
    console.log("✅ ALL TESTS PASSED!");
    console.log("=".repeat(80));
    console.log("\nGoogle Sheets connection is working correctly!");
    console.log("\nNext steps:");
    console.log("1. Add these values to GitHub Secrets:");
    console.log(`   GOOGLE_SHEET_ID: ${sheetId}`);
    console.log(`   GOOGLE_SERVICE_ACCOUNT_EMAIL: ${serviceEmail}`);
    console.log(`   GOOGLE_PRIVATE_KEY: (the full private key from JSON)`);
    console.log("\n2. Trigger workflow manually to test");
    console.log("\n3. Check your Google Sheet - data should appear!");

    return true;
  } catch (error) {
    console.log("\n" + "=".repeat(80));
    console.log("❌ CONNECTION TEST FAILED");
    console.log("=".repeat(80));
    console.log(`\nError: ${error.message}`);
    console.log("\nTroubleshooting:");
    
    if (error.message.includes("Permission")) {
      console.log("  → Make sure the sheet is shared with:");
      console.log(`     ${serviceEmail}`);
      console.log("  → Give it 'Editor' permission");
    }
    
    if (error.message.includes("not found") || error.message.includes("404")) {
      console.log("  → Check GOOGLE_SHEET_ID is correct");
      console.log("  → Should be: 1ejqaP2PVv1w1ygkLUocIPDnUrkWl9wtyzCoVrhuCxkQ");
    }
    
    if (error.message.includes("invalid") || error.message.includes("401")) {
      console.log("  → Check GOOGLE_PRIVATE_KEY is correct");
      console.log("  → Should include the full key with \\n characters");
      console.log("  → Make sure it's copied exactly from JSON file");
    }

    console.log("\nFull error details:");
    console.log(error.stack);
    return false;
  }
}

// Run test
testConnection()
  .then((success) => {
    process.exit(success ? 0 : 1);
  })
  .catch((error) => {
    console.error("Fatal error:", error);
    process.exit(1);
  });

