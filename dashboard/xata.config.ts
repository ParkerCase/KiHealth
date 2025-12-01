import { defineConfig } from '@xata.io/client';

export default defineConfig({
  schema: {
    tables: [
      {
        name: 'cancer_rankings',
        columns: [
          { name: 'Rank', type: 'int' },
          { name: 'cancer_type', type: 'text' },
          { name: 'n_cell_lines', type: 'int' },
          { name: 'overall_score', type: 'float' },
          { name: 'confidence_tier', type: 'text' },
          { name: 'depmap_score_normalized', type: 'float' },
          { name: 'expression_score_normalized', type: 'float' },
          { name: 'mutation_context_score', type: 'float' },
          { name: 'copy_number_score', type: 'float' },
          { name: 'literature_score_normalized', type: 'float' },
          { name: 'experimental_validation_score', type: 'float' },
          { name: 'n_validated_cell_lines', type: 'float' },
          { name: 'total_sl_hits', type: 'int' },
          { name: 'has_sl_evidence', type: 'bool' },
          { name: 'STK17A_mean', type: 'float' },
          { name: 'STK17B_mean', type: 'float' },
          { name: 'MYLK4_mean', type: 'float' },
          { name: 'TBK1_mean', type: 'float' },
          { name: 'CLK4_mean', type: 'float' },
          { name: 'Cell_Lines', type: 'text' },
        ],
      },
    ],
  },
});

