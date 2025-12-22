/**
 * File-Based Storage System for Node.js
 * Replaces Xata with free file-based storage using JSON files
 * 100% free, version-controlled, perfect for GitHub Actions
 */

const fs = require("fs");
const path = require("path");

class FileStorage {
  constructor(dataDir = "data") {
    this.dataDir = path.join(__dirname, "..", dataDir);
    this.ensureDirectory(this.dataDir);
  }

  ensureDirectory(dir) {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  }

  // Generic table storage
  getTablePath(tableName) {
    const tableDir = path.join(this.dataDir, tableName);
    this.ensureDirectory(tableDir);
    return tableDir;
  }

  getRecordPath(tableName, id) {
    const tableDir = this.getTablePath(tableName);
    // Use subdirectories to avoid too many files in one directory
    const subdir = id.substring(0, 2) || "00";
    const subdirPath = path.join(tableDir, subdir);
    this.ensureDirectory(subdirPath);
    return path.join(subdirPath, `${id}.json`);
  }

  getIndexPath(tableName) {
    return path.join(this.getTablePath(tableName), "index.json");
  }

  loadIndex(tableName) {
    const indexPath = this.getIndexPath(tableName);
    if (fs.existsSync(indexPath)) {
      try {
        return JSON.parse(fs.readFileSync(indexPath, "utf8"));
      } catch (e) {
        return {};
      }
    }
    return {};
  }

  saveIndex(tableName, index) {
    const indexPath = this.getIndexPath(tableName);
    fs.writeFileSync(indexPath, JSON.stringify(index, null, 2), "utf8");
  }

  async get(tableName, id) {
    const recordPath = this.getRecordPath(tableName, id);
    if (!fs.existsSync(recordPath)) {
      return null;
    }
    try {
      return JSON.parse(fs.readFileSync(recordPath, "utf8"));
    } catch (e) {
      return null;
    }
  }

  async create(tableName, record) {
    if (!record.id) {
      throw new Error("Record must have an 'id' field");
    }

    const recordPath = this.getRecordPath(tableName, record.id);
    const now = new Date().toISOString();

    // Load existing if it exists (for update)
    const existing = await this.get(tableName, record.id);
    if (existing) {
      // Update existing
      const updated = {
        ...existing,
        ...record,
        updated_at: now,
      };
      fs.writeFileSync(
        recordPath,
        JSON.stringify(updated, null, 2),
        "utf8"
      );

      // Update index
      const index = this.loadIndex(tableName);
      index[record.id] = {
        id: record.id,
        title: updated.title || updated.name || "",
        updated_at: now,
      };
      this.saveIndex(tableName, index);

      return updated;
    } else {
      // Create new
      const newRecord = {
        ...record,
        created_at: now,
        updated_at: now,
      };
      fs.writeFileSync(
        recordPath,
        JSON.stringify(newRecord, null, 2),
        "utf8"
      );

      // Update index
      const index = this.loadIndex(tableName);
      index[record.id] = {
        id: record.id,
        title: newRecord.title || newRecord.name || "",
        created_at: now,
        updated_at: now,
      };
      this.saveIndex(tableName, index);

      return newRecord;
    }
  }

  async update(tableName, id, updates) {
    const existing = await this.get(tableName, id);
    if (!existing) {
      throw new Error(`Record ${id} not found in table ${tableName}`);
    }

    const updated = {
      ...existing,
      ...updates,
      updated_at: new Date().toISOString(),
    };

    const recordPath = this.getRecordPath(tableName, id);
    fs.writeFileSync(recordPath, JSON.stringify(updated, null, 2), "utf8");

    // Update index
    const index = this.loadIndex(tableName);
    if (index[id]) {
      index[id].updated_at = updated.updated_at;
      if (updated.title) index[id].title = updated.title;
      if (updated.name) index[id].title = updated.name;
    }
    this.saveIndex(tableName, index);

    return updated;
  }

  async query(tableName, filterFunc = null, limit = 1000) {
    const index = this.loadIndex(tableName);
    const results = [];
    let count = 0;

    for (const id in index) {
      if (count >= limit) break;

      const record = await this.get(tableName, id);
      if (!record) continue;

      if (!filterFunc || filterFunc(record)) {
        results.push(record);
        count++;
      }
    }

    return results;
  }
}

// Xata-compatible API wrapper
class XataCompatibleClient {
  constructor() {
    this.storage = new FileStorage();
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
    if (!record.id && !record.pmid) {
      throw new Error("Record must have 'id' or 'pmid' field");
    }
    const id = record.id || record.pmid || record.entrez_id;
    return await this.storage.create(this.tableName, { ...record, id });
  }

  async update(id, updates) {
    return await this.storage.update(this.tableName, id, updates);
  }

  async filter(filterObj) {
    // Support filtering by field
    return {
      getFirst: async () => {
        const allRecords = await this.storage.query(this.tableName);
        // Simple filter: find first record matching filterObj
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
        // Filter records
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
  // Always use file storage (no API key needed)
  return new XataCompatibleClient();
}

module.exports = { FileStorage, getXataClient, XataCompatibleClient };

