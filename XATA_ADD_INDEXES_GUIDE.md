# How to Add Indexes in Xata.io

## Quick Steps

### Method 1: Via Schema Editor (Recommended)

1. **Go to your table** (e.g., `cancer_rankings`)
2. **Click on "Schema" or "Schema & migrations"** in the left sidebar
3. **Find the column** you want to index (e.g., `cancer_type`)
4. **Click on the column** to open its settings
5. **Toggle "Index"** or check the "Index" checkbox
6. **Save** the schema changes

### Method 2: Via Column Settings

1. **Go to your table** (e.g., `cancer_rankings`)
2. **Click on the column header** (e.g., `cancer_type`)
3. **Look for "Index" option** in the column menu
4. **Enable indexing** for that column
5. **Save** changes

---

## Recommended Indexes for Each Table

### 1. **cancer_rankings** Table

Add indexes on:

- ✅ `cancer_type` - For filtering by cancer type
- ✅ `overall_score` - For sorting/ranking queries
- ✅ `has_sl_evidence` - For filtering cancers with synthetic lethality

**Why these?**

- `cancer_type`: Most common filter (e.g., "Show me AML")
- `overall_score`: Used for sorting (e.g., "Top 10 cancers")
- `has_sl_evidence`: Boolean filter (e.g., "Cancers with SL")

### 2. **target_rankings** Table

Add indexes on:

- ✅ `target` - For filtering by target (STK17A, STK17B, etc.)
- ✅ `Cancer` - For filtering by cancer type
- ✅ Composite index on `(target, Cancer)` - For combined queries

**Why these?**

- `target`: Filter by specific target (e.g., "All STK17A data")
- `Cancer`: Filter by cancer type
- Composite: For queries like "STK17A in AML"

### 3. **synthetic_lethality** Table

Add indexes on:

- ✅ `target` - For filtering by target
- ✅ `mutation` - For filtering by mutation
- ✅ `is_synthetic_lethal` - For filtering true hits
- ✅ Composite index on `(target, mutation)` - For unique lookups

**Why these?**

- `target`: "All CLK4 synthetic lethality"
- `mutation`: "All NRAS interactions"
- `is_synthetic_lethal`: "Only true hits"
- Composite: Unique mutation × target pairs

### 4. **cell_lines** Table

Add indexes on:

- ✅ `cell_line` - Primary lookup (unique identifier)
- ✅ `cancer_type` - For filtering by cancer
- ✅ `most_dependent_target` - For filtering by target

**Why these?**

- `cell_line`: Direct lookups (e.g., "Find MV411")
- `cancer_type`: "All AML cell lines"
- `most_dependent_target`: "Cell lines most dependent on CLK4"

---

## Step-by-Step: Adding an Index in Xata

### Example: Adding Index to `cancer_type` in `cancer_rankings`

1. **Navigate to your table**

   - Click on `cancer_rankings` in the left sidebar

2. **Open Schema Editor**

   - Click "Schema" or "Schema & migrations" in the left sidebar
   - OR click the "Schema" tab at the top of the table view

3. **Find the column**

   - Scroll to find `cancer_type` column
   - Click on the column name or settings icon

4. **Enable Index**

   - Look for "Index" toggle/checkbox
   - Turn it ON or check the box
   - You may see options like:
     - "Index" (simple index)
     - "Unique index" (if values are unique)
     - "Full-text search" (for text search)

5. **Save Changes**

   - Click "Save" or "Apply" button
   - Xata will create the index (may take a few seconds)

6. **Verify**
   - The column should show an index icon (usually a small key or index symbol)
   - Or you'll see "Indexed" label next to the column

---

## Visual Guide (What to Look For)

### In Schema View:

```
Column Name        Type    Index
─────────────────────────────────
cancer_type       text    ✓ (indexed)
overall_score     float   ✓ (indexed)
n_cell_lines      int     (not indexed)
```

### In Column Settings:

```
cancer_type
├─ Type: text
├─ Index: ✓ Enabled
└─ [Save] button
```

---

## Composite Indexes (Advanced)

For queries that filter on multiple columns:

### Example: `(target, Cancer)` in `target_rankings`

1. **Go to Schema Editor**
2. **Look for "Indexes" section** (may be separate from columns)
3. **Click "Add Index" or "Create Index"**
4. **Select columns**: Choose `target` and `Cancer`
5. **Set order**: Usually `target` first, then `Cancer`
6. **Save**

**When to use composite indexes:**

- Queries like: `WHERE target = 'STK17A' AND Cancer = 'Acute Myeloid Leukemia'`
- More efficient than separate indexes for multi-column filters

---

## Performance Tips

### ✅ DO Index:

- Columns used in `WHERE` clauses frequently
- Columns used in `ORDER BY` frequently
- Foreign key columns (for joins)
- Boolean columns used for filtering

### ❌ DON'T Index:

- Columns rarely queried
- Columns with very few unique values (low cardinality)
- Text columns that are very long (unless using full-text search)
- Columns that change frequently (updates are slower with indexes)

### For Your Tables:

- **Index the key filter columns** (cancer_type, target, mutation)
- **Index sort columns** (overall_score)
- **Index boolean filters** (has_sl_evidence, is_synthetic_lethal)
- **Don't index** large text fields like `Cell_Lines` (unless you need to search within them)

---

## Quick Checklist

After importing each table, add these indexes:

### cancer_rankings

- [ ] Index on `cancer_type`
- [ ] Index on `overall_score`
- [ ] Index on `has_sl_evidence`

### target_rankings

- [ ] Index on `target`
- [ ] Index on `Cancer`
- [ ] (Optional) Composite index on `(target, Cancer)`

### synthetic_lethality

- [ ] Index on `target`
- [ ] Index on `mutation`
- [ ] Index on `is_synthetic_lethal`
- [ ] (Optional) Composite index on `(target, mutation)`

### cell_lines

- [ ] Index on `cell_line`
- [ ] Index on `cancer_type`
- [ ] Index on `most_dependent_target`

---

## Troubleshooting

### "Index already exists"

- The column may already be indexed
- Check the column settings to confirm

### "Cannot create index"

- Some columns can't be indexed (e.g., very large text fields)
- Try a different column or contact Xata support

### "Index creation in progress"

- Large tables may take time to index
- Wait a few minutes and check again

---

## Testing Your Indexes

After adding indexes, test with queries:

```sql
-- Should be fast with index on cancer_type
SELECT * FROM cancer_rankings
WHERE cancer_type = 'Acute Myeloid Leukemia';

-- Should be fast with index on overall_score
SELECT * FROM cancer_rankings
ORDER BY overall_score DESC
LIMIT 10;

-- Should be fast with index on target
SELECT * FROM target_rankings
WHERE target = 'STK17A';
```

If queries are still slow, check:

1. Index was created successfully
2. Query is using the index (check query plan if available)
3. Table size (very large tables may need time to build indexes)

---

**Note**: Index creation is usually instant for small tables (< 1000 rows) but may take a few minutes for larger tables. Xata will show progress if indexing takes time.
