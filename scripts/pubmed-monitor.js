#!/usr/bin/env node

/**
 * PubMed Monitoring System - Two-Stage Filtering
 *
 * STAGE 1: Fast Keyword Filtering (FREE)
 * - Searches PubMed for articles
 * - Applies keyword scoring (no AI)
 * - Only saves papers with keyword_score >= 0.3
 *
 * Monitors PubMed for new articles about:
 * - Target genes: STK17A, MYLK4, TBK1, CLK4
 * - Top 20 cancer types from rankings
 * - Combination queries
 *
 * Stores results in Xata 'papers' table
 */

require("dotenv").config();
const axios = require("axios");
const { buildClient } = require("@xata.io/client");
const fs = require("fs");
const path = require("path");

// Configuration
const TARGET_GENES = ["STK17A", "MYLK4", "TBK1", "CLK4", "STK17B"];
const TOP_CANCER_TYPES = [
  "Acute Myeloid Leukemia",
  "Diffuse Glioma",
  "Extra Gonadal Germ Cell Tumor",
  "Melanoma",
  "Esophagogastric Adenocarcinoma",
  "Non-Small Cell Lung Cancer",
  "Mature T and NK Neoplasms",
  "Colorectal Adenocarcinoma",
  "Endometrial Carcinoma",
  "Head and Neck Squamous Cell Carcinoma",
  "Leiomyosarcoma",
  "Bladder Urothelial Carcinoma",
  "Ovarian Epithelial Tumor",
  "Pancreatic Adenocarcinoma",
  "Ocular Melanoma",
  "B-Cell Acute Lymphoblastic Leukemia",
  "Mature B-Cell Neoplasms",
  "Myeloproliferative Neoplasms",
  "Lung Neuroendocrine Tumor",
  "Osteosarcoma",
];

const DAYS_BACK = 30;
const MAX_ARTICLES_PER_SEARCH = 50;
const MAX_REQUESTS_PER_SECOND = 3;
const MAX_RETRIES = 3;
const KEYWORD_SCORE_THRESHOLD = 0.3; // Only save papers with score >= 0.3

// Setup logging
const logDir = path.join(__dirname, "..", "logs");
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}
const logFile = path.join(
  logDir,
  `pubmed-${new Date().toISOString().split("T")[0]}.log`
);

function log(message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}\n`;
  console.log(message);
  fs.appendFileSync(logFile, logMessage);
}

// Initialize Xata client
function getXataClient() {
  if (!process.env.XATA_API_KEY) {
    throw new Error("XATA_API_KEY is not set in environment variables");
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

// STAGE 1: Keyword Scoring (FREE, no AI)
function calculateKeywordScore(title, abstract) {
  let score = 0.0;
  const text = `${title} ${abstract || ""}`.toLowerCase();

  // Check for exact target gene names in title
  for (const gene of TARGET_GENES) {
    if (title.toLowerCase().includes(gene.toLowerCase())) {
      score += 0.2;
      break; // Only count once
    }
  }

  // Count target genes in abstract
  let geneCount = 0;
  for (const gene of TARGET_GENES) {
    if (text.includes(gene.toLowerCase())) {
      geneCount++;
    }
  }
  score += 0.1 * geneCount; // Up to 0.5 for 5 genes

  // Check for key phrases
  if (
    text.includes("kinase inhibitor") ||
    text.includes("synthetic lethality") ||
    text.includes("synthetic lethal")
  ) {
    score += 0.2;
  }

  // Count cancer types mentioned
  let cancerCount = 0;
  for (const cancer of TOP_CANCER_TYPES) {
    if (text.includes(cancer.toLowerCase())) {
      cancerCount++;
    }
  }
  score += 0.1 * Math.min(cancerCount, 3); // Max 0.3 for 3+ cancers

  // Clinical trial indicators
  if (
    text.includes("phase 2") ||
    text.includes("phase 3") ||
    text.includes("phase ii") ||
    text.includes("phase iii") ||
    text.includes("clinical trial")
  ) {
    score += 0.2;
  }

  // Penalize reviews and meta-analyses
  if (
    text.includes("review") ||
    text.includes("meta-analysis") ||
    text.includes("editorial") ||
    text.includes("commentary")
  ) {
    score -= 0.3;
  }

  // Ensure score is between 0 and 1
  return Math.max(0, Math.min(1, score));
}

// PubMed API helper
async function searchPubMed(query, retries = MAX_RETRIES) {
  await rateLimit();

  const baseUrl = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils";
  const searchUrl = `${baseUrl}/esearch.fcgi`;
  const fetchUrl = `${baseUrl}/efetch.fcgi`;

  try {
    // Step 1: Search for article IDs
    const searchParams = new URLSearchParams({
      db: "pubmed",
      term: query,
      retmax: MAX_ARTICLES_PER_SEARCH.toString(),
      retmode: "json",
      sort: "pub_date",
      datetype: "pdat",
      mindate: getDateDaysAgo(DAYS_BACK),
      maxdate: getDateToday(),
    });

    log(`Searching PubMed: ${query}`);
    const searchResponse = await axios.get(
      `${searchUrl}?${searchParams.toString()}`
    );

    if (
      !searchResponse.data.esearchresult ||
      !searchResponse.data.esearchresult.idlist
    ) {
      log(`No results for query: ${query}`);
      return [];
    }

    const pmids = searchResponse.data.esearchresult.idlist;
    log(`Found ${pmids.length} articles for: ${query}`);

    if (pmids.length === 0) {
      return [];
    }

    // Step 2: Fetch article details
    await rateLimit();
    const fetchParams = new URLSearchParams({
      db: "pubmed",
      id: pmids.join(","),
      retmode: "xml",
    });

    const fetchResponse = await axios.get(
      `${fetchUrl}?${fetchParams.toString()}`
    );
    return await parsePubMedXML(fetchResponse.data, pmids);
  } catch (error) {
    if (retries > 0) {
      log(`Error searching PubMed (${retries} retries left): ${error.message}`);
      await new Promise((resolve) => setTimeout(resolve, 2000));
      return searchPubMed(query, retries - 1);
    }
    log(
      `Failed to search PubMed after ${MAX_RETRIES} retries: ${error.message}`
    );
    throw error;
  }
}

// Parse PubMed XML response
async function parsePubMedXML(xmlString, pmids) {
  const parser = require("xml2js");

  return new Promise((resolve, reject) => {
    parser.parseString(xmlString, (err, result) => {
      if (err) {
        log(`Error parsing XML: ${err.message}`);
        resolve([]);
        return;
      }

      const articles = [];
      const pubmedArticles = result.PubmedArticleSet?.PubmedArticle || [];

      pubmedArticles.forEach((article, index) => {
        try {
          const medline = article.MedlineCitation?.[0];
          const pubmed = article.PubmedData?.[0];

          if (!medline || !pubmed) return;

          const pmid =
            medline.PMID?.[0]?._ || medline.PMID?.[0] || pmids[index];
          const articleData = medline.Article?.[0];

          if (!articleData) return;

          // Extract title
          const title = articleData.ArticleTitle?.[0] || "No title";

          // Extract abstract
          let abstract = "";
          if (articleData.Abstract?.[0]?.AbstractText) {
            const abstractParts = articleData.Abstract[0].AbstractText;
            abstract = Array.isArray(abstractParts)
              ? abstractParts
                  .map((part) =>
                    typeof part === "string" ? part : part._ || ""
                  )
                  .join(" ")
              : typeof abstractParts === "string"
              ? abstractParts
              : abstractParts._ || "";
          }

          // Extract authors
          const authors = [];
          if (articleData.AuthorList?.[0]?.Author) {
            articleData.AuthorList[0].Author.forEach((author) => {
              const lastName = author.LastName?.[0] || "";
              const firstName = author.FirstName?.[0] || "";
              const initials = author.Initials?.[0] || "";
              if (lastName) {
                authors.push(`${lastName} ${firstName || initials}`.trim());
              }
            });
          }

          // Extract journal
          const journal = articleData.Journal?.[0]?.Title?.[0] || "Unknown";

          // Extract publication date
          const pubDate =
            articleData.Journal?.[0]?.JournalIssue?.[0]?.PubDate?.[0];
          let publicationDate = null;
          if (pubDate) {
            const year = pubDate.Year?.[0] || new Date().getFullYear();
            const month = pubDate.Month?.[0] || "01";
            const day = pubDate.Day?.[0] || "01";
            publicationDate = new Date(`${year}-${month}-${day}`);
          }

          // STAGE 1: Calculate keyword score
          const keywordScore = calculateKeywordScore(title, abstract);

          // Only include if score meets threshold
          if (keywordScore < KEYWORD_SCORE_THRESHOLD) {
            return; // Skip this article
          }

          // Extract cancer types and target genes from title/abstract
          const text = `${title} ${abstract}`.toLowerCase();
          const cancerTypes = TOP_CANCER_TYPES.filter((cancer) =>
            text.includes(cancer.toLowerCase())
          );
          const targetGenes = TARGET_GENES.filter((gene) =>
            text.includes(gene.toLowerCase())
          );

          articles.push({
            pubmed_id: pmid.toString(),
            title,
            abstract,
            authors: authors.join("; "),
            journal,
            publication_date: publicationDate || new Date(),
            cancer_types: cancerTypes,
            target_genes: targetGenes,
            keyword_score: keywordScore,
            needs_deep_analysis: true,
            ai_analyzed: false,
            relevance_score: null,
            needs_impact_analysis: false,
            impact_analyzed: false,
            is_actionable: false,
            trigger_recalculation: false,
            last_updated: new Date(),
          });
        } catch (error) {
          log(`Error parsing article ${index}: ${error.message}`);
        }
      });

      resolve(articles);
    });
  });
}

// Helper functions
function getDateDaysAgo(days) {
  const date = new Date();
  date.setDate(date.getDate() - days);
  return date.toISOString().split("T")[0].replace(/-/g, "/");
}

function getDateToday() {
  return new Date().toISOString().split("T")[0].replace(/-/g, "/");
}

// Store articles in Xata
async function storeArticles(xata, articles) {
  let newCount = 0;
  let updatedCount = 0;
  let errorCount = 0;
  let skippedCount = 0;

  for (const article of articles) {
    try {
      // Check if article already exists
      const existing = await xata.db.papers
        .filter({ pubmed_id: article.pubmed_id })
        .getFirst();

      if (existing) {
        // Update existing record (only if keyword score improved)
        const existingScore = existing.keyword_score || 0;
        if (article.keyword_score > existingScore) {
          await xata.db.papers.update(existing.id, {
            title: article.title,
            abstract: article.abstract,
            authors: article.authors,
            journal: article.journal,
            publication_date: article.publication_date,
            cancer_types: article.cancer_types,
            target_genes: article.target_genes,
            keyword_score: article.keyword_score,
            needs_deep_analysis: true, // Reset if score improved
            last_updated: new Date(),
          });
          updatedCount++;
        } else {
          skippedCount++;
        }
      } else {
        // Create new record
        await xata.db.papers.create(article);
        newCount++;
      }
    } catch (error) {
      log(`Error storing article ${article.pubmed_id}: ${error.message}`);
      errorCount++;
    }
  }

  return { newCount, updatedCount, errorCount, skippedCount };
}

// Main execution
async function main() {
  log("=".repeat(80));
  log("PubMed Monitoring System - STAGE 1: Keyword Filtering");
  log("=".repeat(80));

  try {
    // Initialize Xata
    const xata = getXataClient();
    log("✓ Connected to Xata");

    // Build search queries
    const queries = [];

    // 1. Target gene queries
    for (const gene of TARGET_GENES) {
      queries.push(gene);
    }

    // 2. Cancer type queries
    for (const cancer of TOP_CANCER_TYPES) {
      queries.push(cancer);
    }

    // 3. Combination queries (target + cancer) - Top 5 only
    for (const gene of TARGET_GENES) {
      for (const cancer of TOP_CANCER_TYPES.slice(0, 5)) {
        queries.push(`${gene} AND ${cancer}`);
      }
    }

    log(`\nTotal queries to execute: ${queries.length}`);

    // Execute searches
    const allArticles = [];
    const seenIds = new Set();
    let totalSearched = 0;

    for (let i = 0; i < queries.length; i++) {
      const query = queries[i];
      log(`\n[${i + 1}/${queries.length}] Processing query: ${query}`);

      try {
        const articles = await searchPubMed(query);
        totalSearched += articles.length;

        for (const article of articles) {
          if (!seenIds.has(article.pubmed_id)) {
            seenIds.add(article.pubmed_id);
            allArticles.push(article);
          }
        }

        // Small delay between queries
        await new Promise((resolve) => setTimeout(resolve, 500));
      } catch (error) {
        log(`Error processing query "${query}": ${error.message}`);
        // Continue with next query
      }
    }

    log(`\nTotal articles found: ${totalSearched}`);
    log(`Unique articles after deduplication: ${allArticles.length}`);

    // Apply keyword filtering
    log(
      `\nApplying keyword filtering (threshold: ${KEYWORD_SCORE_THRESHOLD})...`
    );
    const filteredArticles = allArticles.filter(
      (a) => a.keyword_score >= KEYWORD_SCORE_THRESHOLD
    );

    log(
      `  ✓ Passed keyword filter: ${filteredArticles.length} articles (${(
        (filteredArticles.length / allArticles.length) *
        100
      ).toFixed(1)}%)`
    );

    // Store in Xata
    if (filteredArticles.length > 0) {
      log("\nStoring articles in Xata...");
      const results = await storeArticles(xata, filteredArticles);
      log(`✓ New articles: ${results.newCount}`);
      log(`✓ Updated articles: ${results.updatedCount}`);
      log(`✓ Skipped (lower score): ${results.skippedCount}`);
      log(`✓ Errors: ${results.errorCount}`);
    } else {
      log("\nNo articles passed keyword filter");
    }

    // Summary
    log("\n" + "=".repeat(80));
    log("STAGE 1 SUMMARY");
    log("=".repeat(80));
    log(`Total articles searched: ${totalSearched}`);
    log(`Unique articles: ${allArticles.length}`);
    log(
      `Passed keyword filter (score >= ${KEYWORD_SCORE_THRESHOLD}): ${filteredArticles.length}`
    );
    log(
      `Filter efficiency: ${(
        ((totalSearched - filteredArticles.length) / totalSearched) *
        100
      ).toFixed(1)}% filtered out (FREE keyword matching)`
    );
    log("\n" + "=".repeat(80));
    log("PubMed Monitoring System - Complete");
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

module.exports = { main, searchPubMed, calculateKeywordScore, storeArticles };
