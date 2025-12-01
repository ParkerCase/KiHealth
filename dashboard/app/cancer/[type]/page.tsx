'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';

interface CancerRanking {
  Rank: number;
  cancer_type: string;
  n_cell_lines: number;
  overall_score: number;
  confidence_tier: string;
  total_sl_hits: number;
  has_sl_evidence: boolean;
  STK17A_mean: number;
  STK17B_mean: number;
  MYLK4_mean: number;
  TBK1_mean: number;
  CLK4_mean: number;
  Cell_Lines: string;
  depmap_score_normalized: number;
  expression_score_normalized: number;
  mutation_context_score: number;
  copy_number_score: number;
  literature_score_normalized: number;
  experimental_validation_score: number;
}

export default function CancerDetailPage() {
  const params = useParams();
  const router = useRouter();
  const cancerType = decodeURIComponent(params.type as string);
  const [cancer, setCancer] = useState<CancerRanking | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCancerData();
  }, [cancerType]);

  const fetchCancerData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/rankings');
      if (response.ok) {
        const data = await response.json();
        const found = data.find((c: CancerRanking) => c.cancer_type === cancerType);
        setCancer(found || null);
      }
    } catch (error) {
      console.error('Error fetching cancer data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading cancer details...</p>
        </div>
      </div>
    );
  }

  if (!cancer) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Cancer Type Not Found</h1>
          <Link href="/" className="text-blue-600 hover:text-blue-700">
            ← Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const targets = [
    { name: 'STK17A', mean: cancer.STK17A_mean, color: 'blue' },
    { name: 'STK17B', mean: cancer.STK17B_mean, color: 'green' },
    { name: 'MYLK4', mean: cancer.MYLK4_mean, color: 'purple' },
    { name: 'TBK1', mean: cancer.TBK1_mean, color: 'orange' },
    { name: 'CLK4', mean: cancer.CLK4_mean, color: 'red' },
  ].sort((a, b) => a.mean - b.mean);

  const formatScore = (score: number) => score?.toFixed(4) || 'N/A';

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <Link href="/" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
            ← Back to Dashboard
          </Link>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{cancer.cancer_type}</h1>
              <p className="text-gray-600 mt-2">Rank #{cancer.Rank} • {cancer.n_cell_lines} cell lines</p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-blue-600">{formatScore(cancer.overall_score)}</div>
              <span className={`px-3 py-1 text-sm font-semibold rounded-full ${
                cancer.confidence_tier === 'HIGH' ? 'bg-green-100 text-green-800' :
                cancer.confidence_tier === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {cancer.confidence_tier}
              </span>
            </div>
          </div>
        </div>

        {/* Target Scores */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Target Dependency Scores</h2>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {targets.map((target) => (
              <div
                key={target.name}
                className={`p-4 rounded-lg border-2 ${
                  target.mean < 0
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 bg-gray-50'
                }`}
              >
                <div className="text-sm font-medium text-gray-600 mb-1">{target.name}</div>
                <div className={`text-2xl font-bold ${
                  target.mean < 0 ? 'text-blue-600' : 'text-gray-600'
                }`}>
                  {formatScore(target.mean)}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {target.mean < 0 ? 'Dependent' : 'Not Dependent'}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Evidence Scores */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Evidence Streams</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">DepMap Score</span>
                <span className="font-semibold">{formatScore(cancer.depmap_score_normalized)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Expression Score</span>
                <span className="font-semibold">{formatScore(cancer.expression_score_normalized)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Mutation Context</span>
                <span className="font-semibold">{formatScore(cancer.mutation_context_score)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Copy Number</span>
                <span className="font-semibold">{formatScore(cancer.copy_number_score)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Literature</span>
                <span className="font-semibold">{formatScore(cancer.literature_score_normalized)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Experimental Validation</span>
                <span className="font-semibold">{formatScore(cancer.experimental_validation_score)}</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Synthetic Lethality</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Total SL Hits</span>
                <span className="font-semibold text-green-600">
                  {cancer.has_sl_evidence ? cancer.total_sl_hits : 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Has SL Evidence</span>
                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                  cancer.has_sl_evidence ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {cancer.has_sl_evidence ? 'Yes' : 'No'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Cell Lines */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Cell Lines ({cancer.n_cell_lines})</h3>
          <div className="flex flex-wrap gap-2">
            {cancer.Cell_Lines?.split(',').map((line, idx) => (
              <span
                key={idx}
                className="px-3 py-1 bg-gray-100 text-gray-700 rounded-lg text-sm"
              >
                {line.trim()}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

