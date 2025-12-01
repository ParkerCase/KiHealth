# Xata Tables Schema - UPDATED for Two-Stage System

## Table 1: `papers` (UPDATED)

**Purpose**: Store PubMed articles with two-stage filtering

### Updated Schema:

```json
{
  "name": "papers",
  "columns": [
    {
      "name": "pubmed_id",
      "type": "string",
      "unique": true
    },
    {
      "name": "title",
      "type": "text"
    },
    {
      "name": "abstract",
      "type": "text"
    },
    {
      "name": "authors",
      "type": "text"
    },
    {
      "name": "journal",
      "type": "string"
    },
    {
      "name": "publication_date",
      "type": "datetime"
    },
    {
      "name": "cancer_types",
      "type": "multiple"
    },
    {
      "name": "target_genes",
      "type": "multiple"
    },
    {
      "name": "keyword_score",
      "type": "float"
    },
    {
      "name": "needs_deep_analysis",
      "type": "bool"
    },
    {
      "name": "ai_analyzed",
      "type": "bool"
    },
    {
      "name": "relevance_score",
      "type": "float"
    },
    {
      "name": "needs_impact_analysis",
      "type": "bool"
    },
    {
      "name": "impact_analyzed",
      "type": "bool"
    },
    {
      "name": "is_actionable",
      "type": "bool"
    },
    {
      "name": "trigger_recalculation",
      "type": "bool"
    },
    {
      "name": "citation_count",
      "type": "int"
    },
    {
      "name": "last_updated",
      "type": "datetime"
    },
    {
      "name": "ai_insights",
      "type": "text"
    },
    {
      "name": "key_findings",
      "type": "text"
    }
  ]
}
```

## Table 2: `lincs_data` (Unchanged)

Same as before - see `XATA_TABLES_SCHEMA.md`

## Table 3: `recalculation_queue` (NEW)

**Purpose**: Queue papers that require ranking recalculation

### Schema:

```json
{
  "name": "recalculation_queue",
  "columns": [
    {
      "name": "paper_id",
      "type": "string"
    },
    {
      "name": "reason",
      "type": "text"
    },
    {
      "name": "created_at",
      "type": "datetime"
    },
    {
      "name": "processed",
      "type": "bool"
    }
  ]
}
```

## Table 4: `ranking_history` (NEW)

**Purpose**: Track changes in cancer rankings

### Schema:

```json
{
  "name": "ranking_history",
  "columns": [
    {
      "name": "cancer_type",
      "type": "string"
    },
    {
      "name": "old_rank",
      "type": "int"
    },
    {
      "name": "new_rank",
      "type": "int"
    },
    {
      "name": "old_score",
      "type": "float"
    },
    {
      "name": "new_score",
      "type": "float"
    },
    {
      "name": "change_reason",
      "type": "text"
    },
    {
      "name": "updated_at",
      "type": "datetime"
    }
  ]
}
```

## Table 5: `dashboard_alerts` (NEW)

**Purpose**: Store alerts for the dashboard UI

### Schema:

```json
{
  "name": "dashboard_alerts",
  "columns": [
    {
      "name": "message",
      "type": "text"
    },
    {
      "name": "change_count",
      "type": "int"
    },
    {
      "name": "changes",
      "type": "text"
    },
    {
      "name": "created_at",
      "type": "datetime"
    },
    {
      "name": "read",
      "type": "bool"
    }
  ]
}
```

## CSV Files for Import

1. **`scripts/papers.csv`** - Updated with new columns
2. **`scripts/lincs_data.csv`** - Unchanged
3. **`scripts/recalculation_queue.csv`** - New (empty)
4. **`scripts/ranking_history.csv`** - New (empty)
5. **`scripts/dashboard_alerts.csv`** - New (empty)
