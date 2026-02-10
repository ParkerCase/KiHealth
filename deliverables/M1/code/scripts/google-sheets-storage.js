/**
 * Google Sheets Storage System
 * Replaces file storage with Google Sheets for easy monitoring
 * 100% free, easy to view and filter data
 */

const { GoogleSpreadsheet } = require("google-spreadsheet");
const { JWT } = require("google-auth-library");

class GoogleSheetsStorage {
  constructor() {
    this.doc = null;
    this.sheets = {};
    this.initialized = false;
  }

  async initialize() {
    if (this.initialized) return;

    const sheetId = process.env.GOOGLE_SHEET_ID;
    const serviceAccountEmail = process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL;
    const privateKey = process.env.GOOGLE_PRIVATE_KEY?.replace(/\\n/g, "\n");

    if (!sheetId || !serviceAccountEmail || !privateKey) {
      throw new Error(
        "Google Sheets credentials not found. Set GOOGLE_SHEET_ID, GOOGLE_SERVICE_ACCOUNT_EMAIL, and GOOGLE_PRIVATE_KEY"
      );
    }

    // Initialize auth
    const serviceAccountAuth = new JWT({
      email: serviceAccountEmail,
      key: privateKey,
      scopes: ["https://www.googleapis.com/auth/spreadsheets"],
    });

    // Initialize the sheet
    this.doc = new GoogleSpreadsheet(sheetId, serviceAccountAuth);
    await this.doc.loadInfo();

    this.initialized = true;
  }

  async getOrCreateSheet(sheetName) {
    await this.initialize();

    if (this.sheets[sheetName]) {
      return this.sheets[sheetName];
    }

    let sheet = this.doc.sheetsByTitle[sheetName];
    if (!sheet) {
      // Create sheet if it doesn't exist
      sheet = await this.doc.addSheet({
        title: sheetName,
        headerValues: this.getHeadersForTable(sheetName),
      });
    } else {
      await sheet.loadHeaderRow();
    }

    this.sheets[sheetName] = sheet;
    return sheet;
  }

  getHeadersForTable(tableName) {
    if (tableName === "papers") {
      return [
        "id",
        "pubmed_id",
        "title",
        "abstract",
        "authors",
        "journal",
        "publication_date",
        "cancer_types",
        "target_genes",
        "keyword_score",
        "relevance_score",
        "needs_deep_analysis",
        "is_actionable",
        "created_at",
        "updated_at",
      ];
    } else if (tableName === "lincs_data") {
      return [
        "id",
        "lincs_id",
        "compound_name",
        "target_gene",
        "cell_line",
        "efficacy_score",
        "interaction_type",
        "data_source",
        "created_at",
        "updated_at",
      ];
    }
    return ["id", "data", "created_at", "updated_at"];
  }

  async get(tableName, id) {
    const sheet = await this.getOrCreateSheet(tableName);
    const rows = await sheet.getRows();

    const row = rows.find((r) => r.get("id") === id);
    if (!row) return null;

    return this.rowToObject(row, sheet.headerValues);
  }

  async create(tableName, record) {
    const sheet = await this.getOrCreateSheet(tableName);
    const now = new Date().toISOString();

    // Check if exists
    const existing = await this.get(tableName, record.id || record.pubmed_id || record.lincs_id);
    if (existing) {
      return await this.update(tableName, record.id || record.pubmed_id || record.lincs_id, record);
    }

    // Create new
    const data = {
      ...record,
      id: record.id || record.pubmed_id || record.lincs_id,
      created_at: now,
      updated_at: now,
    };

    // Convert arrays/objects to JSON strings for Google Sheets
    const rowData = {};
    for (const header of sheet.headerValues) {
      const value = data[header];
      if (value === undefined || value === null) {
        rowData[header] = "";
      } else if (Array.isArray(value)) {
        rowData[header] = JSON.stringify(value);
      } else if (typeof value === "object") {
        rowData[header] = JSON.stringify(value);
      } else {
        rowData[header] = String(value);
      }
    }

    await sheet.addRow(rowData);
    return data;
  }

  async update(tableName, id, updates) {
    const sheet = await this.getOrCreateSheet(tableName);
    const rows = await sheet.getRows();

    const row = rows.find((r) => r.get("id") === id);
    if (!row) {
      throw new Error(`Record ${id} not found in ${tableName}`);
    }

    const now = new Date().toISOString();
    const updated = {
      ...this.rowToObject(row, sheet.headerValues),
      ...updates,
      updated_at: now,
    };

    // Update row
    for (const header of sheet.headerValues) {
      const value = updated[header];
      if (value === undefined || value === null) {
        row.set(header, "");
      } else if (Array.isArray(value) || typeof value === "object") {
        row.set(header, JSON.stringify(value));
      } else {
        row.set(header, String(value));
      }
    }

    await row.save();
    return updated;
  }

  async query(tableName, filterFunc = null, limit = 1000) {
    const sheet = await this.getOrCreateSheet(tableName);
    const rows = await sheet.getRows();

    const results = [];
    for (const row of rows) {
      if (results.length >= limit) break;

      const record = this.rowToObject(row, sheet.headerValues);
      if (!filterFunc || filterFunc(record)) {
        results.push(record);
      }
    }

    return results;
  }

  rowToObject(row, headers) {
    const obj = {};
    for (const header of headers) {
      const value = row.get(header);
      if (value === "" || value === null) {
        obj[header] = null;
      } else {
        // Try to parse JSON
        try {
          obj[header] = JSON.parse(value);
        } catch {
          obj[header] = value;
        }
      }
    }
    return obj;
  }
}

// Xata-compatible API wrapper
class XataCompatibleClient {
  constructor() {
    this.storage = new GoogleSheetsStorage();
  }

  get db() {
    return {
      papers: new TableWrapper(this.storage, "papers"),
      lincs_data: new TableWrapper(this.storage, "lincs_data"),
    };
  }
}

class TableWrapper {
  constructor(storage, tableName) {
    this.storage = storage;
    this.tableName = tableName;
  }

  async get(id) {
    const record = await this.storage.get(this.tableName, id);
    return record ? { id: record.id, ...record } : null;
  }

  async create(record) {
    const id = record.id || record.pubmed_id || record.lincs_id;
    return await this.storage.create(this.tableName, { ...record, id });
  }

  async update(id, updates) {
    return await this.storage.update(this.tableName, id, updates);
  }

  async filter(filterObj) {
    return {
      getFirst: async () => {
        const allRecords = await this.storage.query(this.tableName);
        for (const record of allRecords) {
          let matches = true;
          for (const key in filterObj) {
            if (record[key] !== filterObj[key]) {
              matches = false;
              break;
            }
          }
          if (matches) {
            return { id: record.id, ...record };
          }
        }
        return null;
      },
      getMany: async () => {
        const allRecords = await this.storage.query(this.tableName);
        return allRecords.filter((record) => {
          for (const key in filterObj) {
            if (record[key] !== filterObj[key]) {
              return false;
            }
          }
          return true;
        });
      },
    };
  }
}

// Export Xata-compatible client
function getXataClient() {
  // Use Google Sheets if credentials available, otherwise fall back to file storage
  if (
    process.env.GOOGLE_SHEET_ID &&
    process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL &&
    process.env.GOOGLE_PRIVATE_KEY
  ) {
    return new XataCompatibleClient();
  } else {
    // Fall back to file storage
    const { getXataClient: getFileStorage } = require("./file-storage");
    return getFileStorage();
  }
}

module.exports = { GoogleSheetsStorage, getXataClient, XataCompatibleClient };

