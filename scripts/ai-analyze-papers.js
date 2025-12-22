#!/usr/bin/env node

/**
 * AI-Powered Paper Analysis - Two-Stage System
 *
 * STAGE 1: Quick Relevance Scoring (cheap, fast)
 * - Analyzes all papers that need deep analysis
 * - Uses minimal prompt for speed/cost
 * - Flags papers with relevance_score >= 0.7 for Stage 2
 *
 * STAGE 2: Deep Impact Analysis (expensive, thorough)
 * - Only analyzes actionable papers (relevance >= 0.7)
 * - Full abstract analysis with detailed prompt
 * - Determines if ranking update is needed
 *
 * Supports both Anthropic Claude and OpenAI GPT-4
 */

require("dotenv").config();
const { getXataClient } = require("./file-storage"); // Use file storage instead
const Anthropic = require("@anthropic-ai/sdk");
const OpenAI = require("openai");
const fs = require("fs");
const path = require("path");

// Configuration
const TARGET_GENES = ["STK17A", "STK17B", "MYLK4", "TBK1", "CLK4"];
const BATCH_SIZE_STAGE1 = 20; // Process 20 papers at once for quick scoring
const BATCH_SIZE_STAGE2 = 5; // Process 5 papers at once for deep analysis
const AI_PROVIDER = process.env.AI_PROVIDER || "anthropic";
const REQUESTS_PER_SECOND_STAGE1 = AI_PROVIDER === "openai" ? 2 : 1;
const REQUESTS_PER_SECOND_STAGE2 = 0.5; // Slower for deep analysis
const MAX_RETRIES = 3;
const RELEVANCE_THRESHOLD = 0.7; // Papers with score >= 0.7 go to Stage 2

// Setup logging
const logDir = path.join(__dirname, "..", "logs");
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}
const logFile = path.join(
  logDir,
  `ai-analyze-${new Date().toISOString().split("T")[0]}.log`
);

function log(message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}\n`;
  console.log(message);
  fs.appendFileSync(logFile, logMessage);
}

// Xata client is now imported from file-storage.js (file-based, no API key needed)

// Initialize AI client (supports both Claude and OpenAI)
function getAIClient() {
  if (AI_PROVIDER === "openai") {
    if (!process.env.OPENAI_API_KEY) {
      throw new Error("OPENAI_API_KEY is not set in environment variables");
    }
    return {
      provider: "openai",
      client: new OpenAI({
        apiKey: process.env.OPENAI_API_KEY,
      }),
    };
  } else {
    if (!process.env.ANTHROPIC_API_KEY) {
      throw new Error("ANTHROPIC_API_KEY is not set in environment variables");
    }
    return {
      provider: "anthropic",
      client: new Anthropic({
        apiKey: process.env.ANTHROPIC_API_KEY,
      }),
    };
  }
}

// Rate limiting helper
let lastRequestTime = 0;
let currentRateLimit = REQUESTS_PER_SECOND_STAGE1;

function setRateLimit(requestsPerSecond) {
  currentRateLimit = requestsPerSecond;
}

async function rateLimit() {
  const now = Date.now();
  const timeSinceLastRequest = now - lastRequestTime;
  const minInterval = 1000 / currentRateLimit;

  if (timeSinceLastRequest < minInterval) {
    await new Promise((resolve) =>
      setTimeout(resolve, minInterval - timeSinceLastRequest)
    );
  }
  lastRequestTime = Date.now();
}

// STAGE 1: Quick Relevance Scoring (cheap, fast)
async function quickRelevanceScore(aiClient, paper, retries = MAX_RETRIES) {
  await rateLimit();

  const prompt = `Rate this paper's relevance to multi-target kinase inhibitor research in cancer.

Targets: ${TARGET_GENES.join(", ")}
Title: ${paper.title || "No title"}

Return only a number 0-1 (0=irrelevant, 1=highly relevant). No explanation, just the number.`;

  try {
    let content;

    if (aiClient.provider === "openai") {
      const response = await aiClient.client.chat.completions.create({
        model: "gpt-4-turbo-preview",
        messages: [
          {
            role: "system",
            content:
              "You are a scientific research analyst. Return only a number between 0 and 1, nothing else.",
          },
          {
            role: "user",
            content: prompt,
          },
        ],
        max_tokens: 10, // Very short response
        temperature: 0.3,
      });
      content = response.choices[0].message.content;
    } else {
      // Claude
      const message = await aiClient.client.messages.create({
        model: "claude-sonnet-4-20250514",
        max_tokens: 10,
        messages: [
          {
            role: "user",
            content: prompt,
          },
        ],
      });
      content = message.content[0].text;
    }

    // Extract number from response
    const match = content.match(/(\d+\.?\d*)/);
    if (match) {
      const score = parseFloat(match[1]);
      return Math.max(0, Math.min(1, score)); // Clamp to 0-1
    }
    return 0.5; // Default if parsing fails
  } catch (error) {
    if (retries > 0) {
      log(
        `Error quick-scoring paper ${paper.pubmed_id} (${retries} retries left): ${error.message}`
      );
      await new Promise((resolve) => setTimeout(resolve, 2000));
      return quickRelevanceScore(aiClient, paper, retries - 1);
    }
    log(`Failed to quick-score paper ${paper.pubmed_id}: ${error.message}`);
    return null;
  }
}

// STAGE 2: Deep Impact Analysis (expensive, thorough)
async function deepImpactAnalysis(
  aiClient,
  paper,
  topCancers,
  retries = MAX_RETRIES
) {
  await rateLimit();

  const prompt = `Analyze this paper for impact on cancer kinase inhibitor research:

Abstract: ${paper.abstract || "No abstract available"}

Our targets: ${TARGET_GENES.join(", ")}
Current top cancers: ${topCancers.slice(0, 10).join(", ")}

Return ONLY valid JSON (no markdown, no code blocks):
{
  "relevance_score": 0-1,
  "key_findings": "2-3 sentence summary",
  "cancer_types_mentioned": ["array", "of", "cancer", "types"],
  "targets_mentioned": ["array", "of", "target", "genes"],
  "contains_ic50_data": boolean,
  "contradicts_existing_data": boolean,
  "suggests_new_indication": boolean,
  "suggests_new_mechanism": boolean,
  "clinical_stage": "preclinical/phase1/phase2/phase3/approved/null",
  "requires_ranking_update": boolean,
  "reason_for_update": "explanation if requires_ranking_update is true"
}`;

  try {
    let content;

    if (aiClient.provider === "openai") {
      const response = await aiClient.client.chat.completions.create({
        model: "gpt-4-turbo-preview",
        messages: [
          {
            role: "system",
            content:
              "You are a scientific research analyst. Always return valid JSON only, no markdown formatting.",
          },
          {
            role: "user",
            content: prompt,
          },
        ],
        response_format: { type: "json_object" },
        max_tokens: 1024,
        temperature: 0.3,
      });
      content = response.choices[0].message.content;
    } else {
      // Claude
      const message = await aiClient.client.messages.create({
        model: "claude-sonnet-4-20250514",
        max_tokens: 1024,
        messages: [
          {
            role: "user",
            content: prompt,
          },
        ],
      });
      content = message.content[0].text;
    }

    // Extract JSON from response
    let jsonStr = content.trim();
    if (jsonStr.startsWith("```json")) {
      jsonStr = jsonStr.replace(/```json\n?/g, "").replace(/```\n?/g, "");
    } else if (jsonStr.startsWith("```")) {
      jsonStr = jsonStr.replace(/```\n?/g, "");
    }

    const analysis = JSON.parse(jsonStr);

    return {
      relevance_score: analysis.relevance_score || 0.0,
      key_findings: analysis.key_findings || "",
      cancer_types_mentioned: analysis.cancer_types_mentioned || [],
      targets_mentioned: analysis.targets_mentioned || [],
      contains_ic50_data: analysis.contains_ic50_data || false,
      contradicts_existing_data: analysis.contradicts_existing_data || false,
      suggests_new_indication: analysis.suggests_new_indication || false,
      suggests_new_mechanism: analysis.suggests_new_mechanism || false,
      clinical_stage: analysis.clinical_stage || null,
      requires_ranking_update: analysis.requires_ranking_update || false,
      reason_for_update: analysis.reason_for_update || "",
    };
  } catch (error) {
    if (retries > 0) {
      log(
        `Error deep-analyzing paper ${paper.pubmed_id} (${retries} retries left): ${error.message}`
      );
      await new Promise((resolve) => setTimeout(resolve, 2000));
      return deepImpactAnalysis(aiClient, paper, topCancers, retries - 1);
    }
    log(`Failed to deep-analyze paper ${paper.pubmed_id}: ${error.message}`);
    return null;
  }
}

// Update paper with Stage 1 results
async function updatePaperStage1(xata, paperId, relevanceScore) {
  try {
    await xata.db.papers.update(paperId, {
      relevance_score: relevanceScore,
      ai_analyzed: true,
      needs_impact_analysis: relevanceScore >= RELEVANCE_THRESHOLD,
      last_updated: new Date(),
    });
    return true;
  } catch (error) {
    log(`Error updating paper ${paperId} (Stage 1): ${error.message}`);
    return false;
  }
}

// Update paper with Stage 2 results
async function updatePaperStage2(xata, paperId, analysis) {
  try {
    await xata.db.papers.update(paperId, {
      relevance_score: analysis.relevance_score,
      key_findings: analysis.key_findings,
      impact_analyzed: true,
      is_actionable: analysis.relevance_score >= RELEVANCE_THRESHOLD,
      trigger_recalculation: analysis.requires_ranking_update || false,
      ai_insights: JSON.stringify({
        cancer_types_mentioned: analysis.cancer_types_mentioned,
        targets_mentioned: analysis.targets_mentioned,
        contains_ic50_data: analysis.contains_ic50_data,
        contradicts_existing_data: analysis.contradicts_existing_data,
        suggests_new_indication: analysis.suggests_new_indication,
        suggests_new_mechanism: analysis.suggests_new_mechanism,
        clinical_stage: analysis.clinical_stage,
        requires_ranking_update: analysis.requires_ranking_update,
        reason_for_update: analysis.reason_for_update,
      }),
      last_updated: new Date(),
    });

    // If requires ranking update, add to recalculation queue
    if (analysis.requires_ranking_update) {
      try {
        await xata.db.recalculation_queue.create({
          paper_id: paperId,
          reason: analysis.reason_for_update,
          created_at: new Date(),
          processed: false,
        });
      } catch (error) {
        // Table might not exist yet, that's okay
        log(`Note: Could not add to recalculation_queue: ${error.message}`);
      }
    }

    return true;
  } catch (error) {
    log(`Error updating paper ${paperId} (Stage 2): ${error.message}`);
    return false;
  }
}

// Get top cancers from Xata
async function getTopCancers(xata) {
  try {
    const rankings = await xata.db.cancer_rankings
      .select(["cancer_type"])
      .sort("overall_score", "desc")
      .getMany({ pagination: { size: 20 } });

    return rankings.map((r) => r.cancer_type);
  } catch (error) {
    log(`Error fetching top cancers: ${error.message}`);
    return [];
  }
}

// Main execution
async function main() {
  log("=".repeat(80));
  log("AI Paper Analysis System - Two-Stage Analysis");
  log("=".repeat(80));

  try {
    // Initialize clients
    const xata = getXataClient();
    const aiClient = getAIClient();
    log(
      `✓ Connected to Xata and ${
        aiClient.provider === "openai" ? "OpenAI GPT-4" : "Anthropic Claude"
      }`
    );

    // Get top cancers for Stage 2 analysis
    log("\nFetching top cancer types...");
    const topCancers = await getTopCancers(xata);
    log(`✓ Loaded ${topCancers.length} top cancer types`);

    // ========================================================================
    // STAGE 1: Quick Relevance Scoring
    // ========================================================================
    log("\n" + "=".repeat(80));
    log("STAGE 1: Quick Relevance Scoring");
    log("=".repeat(80));

    setRateLimit(REQUESTS_PER_SECOND_STAGE1);

    // Fetch papers that need deep analysis
    log("\nFetching papers for Stage 1 analysis...");
    const stage1Papers = await xata.db.papers
      .filter({
        needs_deep_analysis: true,
        ai_analyzed: false,
      })
      .getAll();

    log(`Found ${stage1Papers.length} papers for Stage 1 analysis`);

    if (stage1Papers.length === 0) {
      log("No papers need Stage 1 analysis. Skipping to Stage 2.");
    } else {
      // Process papers in batches
      let analyzed = 0;
      let failed = 0;
      let flaggedForStage2 = 0;

      for (let i = 0; i < stage1Papers.length; i += BATCH_SIZE_STAGE1) {
        const batch = stage1Papers.slice(i, i + BATCH_SIZE_STAGE1);
        log(
          `\nProcessing Stage 1 batch ${
            Math.floor(i / BATCH_SIZE_STAGE1) + 1
          }/${Math.ceil(stage1Papers.length / BATCH_SIZE_STAGE1)}`
        );

        for (const paper of batch) {
          try {
            log(
              `Quick-scoring: ${paper.pubmed_id} - ${paper.title?.substring(
                0,
                50
              )}...`
            );
            const score = await quickRelevanceScore(aiClient, paper);

            if (score !== null) {
              await updatePaperStage1(xata, paper.id, score);
              analyzed++;
              if (score >= RELEVANCE_THRESHOLD) {
                flaggedForStage2++;
                log(`  ✓ Score: ${score.toFixed(2)} → Flagged for Stage 2`);
              } else {
                log(`  ✓ Score: ${score.toFixed(2)}`);
              }
            } else {
              failed++;
            }
          } catch (error) {
            log(`Error processing paper ${paper.pubmed_id}: ${error.message}`);
            failed++;
          }
        }
      }

      log(`\nStage 1 Summary:`);
      log(`  ✓ Analyzed: ${analyzed}`);
      log(`  ✗ Failed: ${failed}`);
      log(`  → Flagged for Stage 2: ${flaggedForStage2}`);
    }

    // ========================================================================
    // STAGE 2: Deep Impact Analysis
    // ========================================================================
    log("\n" + "=".repeat(80));
    log("STAGE 2: Deep Impact Analysis");
    log("=".repeat(80));

    setRateLimit(REQUESTS_PER_SECOND_STAGE2);

    // Fetch papers that need impact analysis
    log("\nFetching papers for Stage 2 analysis...");
    const stage2Papers = await xata.db.papers
      .filter({
        needs_impact_analysis: true,
        impact_analyzed: false,
      })
      .getAll();

    log(`Found ${stage2Papers.length} papers for Stage 2 analysis`);

    if (stage2Papers.length === 0) {
      log("No papers need Stage 2 analysis.");
    } else {
      // Process papers in batches
      let analyzed = 0;
      let failed = 0;
      let actionable = 0;
      let requiresRecalc = 0;

      for (let i = 0; i < stage2Papers.length; i += BATCH_SIZE_STAGE2) {
        const batch = stage2Papers.slice(i, i + BATCH_SIZE_STAGE2);
        log(
          `\nProcessing Stage 2 batch ${
            Math.floor(i / BATCH_SIZE_STAGE2) + 1
          }/${Math.ceil(stage2Papers.length / BATCH_SIZE_STAGE2)}`
        );

        for (const paper of batch) {
          try {
            log(
              `Deep-analyzing: ${paper.pubmed_id} - ${paper.title?.substring(
                0,
                50
              )}...`
            );
            const analysis = await deepImpactAnalysis(
              aiClient,
              paper,
              topCancers
            );

            if (analysis) {
              await updatePaperStage2(xata, paper.id, analysis);
              analyzed++;
              if (analysis.relevance_score >= RELEVANCE_THRESHOLD) {
                actionable++;
              }
              if (analysis.requires_ranking_update) {
                requiresRecalc++;
                log(
                  `  ✓ Score: ${analysis.relevance_score.toFixed(
                    2
                  )} → REQUIRES RECALCULATION`
                );
              } else {
                log(`  ✓ Score: ${analysis.relevance_score.toFixed(2)}`);
              }
            } else {
              failed++;
            }
          } catch (error) {
            log(`Error processing paper ${paper.pubmed_id}: ${error.message}`);
            failed++;
          }
        }
      }

      log(`\nStage 2 Summary:`);
      log(`  ✓ Analyzed: ${analyzed}`);
      log(`  ✗ Failed: ${failed}`);
      log(`  → Actionable papers: ${actionable}`);
      log(`  → Require recalculation: ${requiresRecalc}`);
    }

    log("\n" + "=".repeat(80));
    log("AI Paper Analysis System - Complete");
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

module.exports = {
  main,
  quickRelevanceScore,
  deepImpactAnalysis,
  getAIClient,
};
