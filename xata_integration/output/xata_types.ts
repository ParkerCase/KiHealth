
// Auto-generated Xata types for Next.js
// Location: src/xata.ts

export interface CancerRanking {
  id: string;
  cancer_type: string;
  rank: number;
  overall_score: number;
  confidence_tier: 'HIGH' | 'MEDIUM' | 'LOW';
  depmap_score: number;
  expression_score: number;
  mutation_score: number;
  copy_number_score: number;
  literature_score: number;
  n_cell_lines: number;
  n_validated_lines: number;
  validation_available: boolean;
  significant_sl_hits: number;
  key_findings: string;
  stk17a_score: number;
  mylk4_score: number;
  tbk1_score: number;
  clk4_score: number;
  summary: string;
  last_updated: Date;
}

export interface TargetScore {
  id: string;
  cancer_type: string;
  cancer_rank: number;
  target_gene: string;
  dependency_score: number;
  cancer_overall_score: number;
  confidence_tier: string;
  n_cell_lines: number;
  validation_available: boolean;
  summary: string;
}

export interface SyntheticLethality {
  id: string;
  mutation: string;
  target_gene: string;
  n_mutant_lines: number;
  n_wt_lines: number;
  mutant_mean_score: number;
  wt_mean_score: number;
  effect_size: number;
  p_value: number;
  is_significant: boolean;
  most_dependent_line: string;
  mutant_lines_sample: string[];
  summary: string;
}
