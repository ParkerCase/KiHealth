# Individual Target Rankings - Where Are They?

## ✅ YES - Individual Rankings Are Included!

The **`target_rankings_combined.csv`** file contains **ALL individual 1-77 rankings for each of the 5 targets**.

---

## File Structure

### `target_rankings_combined.csv` (385 rows)

**Contains:**

- ✅ **STK17A**: 77 rows (rankings 1-77, one per cancer type)
- ✅ **STK17B**: 77 rows (rankings 1-77, one per cancer type)
- ✅ **MYLK4**: 77 rows (rankings 1-77, one per cancer type)
- ✅ **TBK1**: 77 rows (rankings 1-77, one per cancer type)
- ✅ **CLK4**: 77 rows (rankings 1-77, one per cancer type)

**Total**: 77 cancers × 5 targets = **385 rows**

---

## How to Use It

### Filter by Target

To get STK17A rankings (1-77):

```sql
SELECT * FROM target_rankings
WHERE target = 'STK17A'
ORDER BY Rank;
```

To get CLK4 rankings (1-77):

```sql
SELECT * FROM target_rankings
WHERE target = 'CLK4'
ORDER BY Rank;
```

### Get Top 10 for Each Target

```sql
-- Top 10 STK17A cancers
SELECT * FROM target_rankings
WHERE target = 'STK17A'
ORDER BY Rank
LIMIT 10;

-- Top 10 CLK4 cancers
SELECT * FROM target_rankings
WHERE target = 'CLK4'
ORDER BY Rank
LIMIT 10;
```

---

## Column Structure

Each row has:

- `target` - Which target (STK17A, STK17B, MYLK4, TBK1, or CLK4)
- `Rank` - Ranking for that specific target (1-77)
- `Cancer` - Cancer type name
- `STK17A_mean`, `STK17A_n`, `STK17A_std`, etc. - Stats for STK17A (only populated when target = STK17A)
- `STK17B_mean`, `STK17B_n`, etc. - Stats for STK17B (only populated when target = STK17B)
- `MYLK4_mean`, etc. - Stats for MYLK4
- `TBK1_mean`, etc. - Stats for TBK1
- `CLK4_mean`, etc. - Stats for CLK4
- `Cell_Lines` - Cell lines for that cancer type
- `Individual_Scores` - Individual cell line scores

**Note**: When `target = 'STK17A'`, only the STK17A columns are populated. The other target columns are empty.

---

## Example Data

### STK17A Rankings (first 3 rows):

```
target: STK17A
Rank: 1, Cancer: "Sarcoma, NOS", STK17A_mean: -0.2439
Rank: 2, Cancer: Poorly Differentiated Thyroid Cancer, STK17A_mean: -0.2201
Rank: 3, Cancer: Mucosal Melanoma of the Vulva/Vagina, STK17A_mean: -0.2064
```

### CLK4 Rankings (first 3 rows):

```
target: CLK4
Rank: 1, Cancer: [different cancer], CLK4_mean: [different value]
Rank: 2, Cancer: [different cancer], CLK4_mean: [different value]
Rank: 3, Cancer: [different cancer], CLK4_mean: [different value]
```

**Each target has its own independent ranking!**

---

## Summary

✅ **YES** - All individual 1-77 rankings for all 5 targets are in:

- **File**: `target_rankings_combined.csv`
- **Table**: `target_rankings` (in Xata)
- **How to access**: Filter by `target` column

You don't need separate files - everything is in one combined table, just filter by the `target` column!
