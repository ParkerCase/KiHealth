# Xata Tables Schema for PubMed + LINCS Monitoring

## Table 1: `papers`

**Purpose**: Store PubMed articles about targets and cancer types

### Schema:

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
      "name": "relevance_score",
      "type": "float"
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

## Table 2: `lincs_data`

**Purpose**: Store LINCS drug-gene interaction data

### Schema:

```json
{
  "name": "lincs_data",
  "columns": [
    {
      "name": "lincs_id",
      "type": "string",
      "unique": true
    },
    {
      "name": "compound_name",
      "type": "string"
    },
    {
      "name": "target_gene",
      "type": "string"
    },
    {
      "name": "cell_line",
      "type": "string"
    },
    {
      "name": "efficacy_score",
      "type": "float"
    },
    {
      "name": "interaction_type",
      "type": "string"
    },
    {
      "name": "data_source",
      "type": "string"
    },
    {
      "name": "last_updated",
      "type": "datetime"
    }
  ]
}
```

## Instructions for Creating Tables in Xata:

1. Go to Xata dashboard
2. Select your database
3. Click "Add Table"
4. Name it `papers`
5. Add columns as specified above
6. Repeat for `lincs_data` table
