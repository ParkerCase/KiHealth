'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import TopCancersChart from './components/TopCancersChart';
import SemanticSearch from './components/SemanticSearch';
import FileUpload from './components/FileUpload';
import MutationContextExplorer from './components/MutationContextExplorer';

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
  // Mutation flags
  has_NRAS?: boolean;
  has_KRAS?: boolean;
  has_BRAF?: boolean;
  has_TP53?: boolean;
  has_PIK3CA?: boolean;
  has_PTEN?: boolean;
  has_EGFR?: boolean;
  has_APC?: boolean;
  has_SMAD4?: boolean;
  has_CDKN2A?: boolean;
  has_RB1?: boolean;
  has_NF1?: boolean;
  has_ARID1A?: boolean;
  has_CTNNB1?: boolean;
  has_IDH1?: boolean;
  has_IDH2?: boolean;
  has_FLT3?: boolean;
  has_NPM1?: boolean;
  has_DNMT3A?: boolean;
  has_TET2?: boolean;
  has_ASXL1?: boolean;
  [key: string]: string | number | boolean | undefined;
}

interface TargetRanking {
  Rank: number;
  Cancer: string;
  target: string;
  STK17A_mean?: number;
  STK17B_mean?: number;
  MYLK4_mean?: number;
  TBK1_mean?: number;
  CLK4_mean?: number;
  [key: string]: string | number | undefined;
}

interface SyntheticLethality {
  mutation: string;
  target: string;
  is_synthetic_lethal: boolean;
  p_value: number;
  mean_diff: number;
  n_mutant: number;
  n_wt: number;
  mutant_mean?: number;
  wt_mean?: number;
  [key: string]: string | number | boolean | undefined;
}

interface CellLine {
  cell_line: string;
  cancer_type: string;
  most_dependent_target: string;
  cancer_rank: number;
}

type TabType = 'overview' | 'cancer-rankings' | 'target-rankings' | 'synthetic-lethality' | 'cell-lines' | 'mutation-explorer' | 'upload';

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [cancerRankings, setCancerRankings] = useState<CancerRanking[]>([]);
  const [targetRankings, setTargetRankings] = useState<TargetRanking[]>([]);
  const [syntheticLethality, setSyntheticLethality] = useState<SyntheticLethality[]>([]);
  const [cellLines, setCellLines] = useState<CellLine[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [semanticTarget, setSemanticTarget] = useState<string | null>(null);
  const [semanticMutation, setSemanticMutation] = useState<string | null>(null);

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      const [cancerRes, targetRes, slRes, cellRes] = await Promise.all([
        fetch('/api/rankings'),
        fetch('/api/target-rankings'),
        fetch('/api/synthetic-lethality'),
        fetch('/api/cell-lines'),
      ]);

      if (cancerRes.ok) {
        const data = await cancerRes.json();
        setCancerRankings(data.sort((a: CancerRanking, b: CancerRanking) => b.overall_score - a.overall_score));
      }
      if (targetRes.ok) {
        const data = await targetRes.json();
        setTargetRankings(data);
      }
      if (slRes.ok) {
        const data = await slRes.json();
        setSyntheticLethality(data);
      }
      if (cellRes.ok) {
        const data = await cellRes.json();
        setCellLines(data);
      }
    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };


  const stats = {
    totalCancers: cancerRankings.filter(c => c.cancer_type !== 'Non-Cancerous').length,
    totalCellLines: cellLines.filter(cl => cl.cancer_type !== 'Non-Cancerous').length,
    totalSLHits: syntheticLethality.filter(sl => sl.is_synthetic_lethal).length,
    totalTargets: new Set(targetRankings.map(t => t.target)).size,
  };

  const filteredCancerRankings = (() => {
    let filtered = cancerRankings.filter(r => r.cancer_type !== 'Non-Cancerous');
    
    // Filter by mutation if specified
    if (semanticMutation) {
      const mutationKey = `has_${semanticMutation}` as keyof CancerRanking;
      filtered = filtered.filter(r => r[mutationKey] === true);
    }
    
    // If semantic search found a target, sort by that target's dependency
    if (semanticTarget) {
      const targetKey = `${semanticTarget}_mean` as keyof CancerRanking;
      filtered = filtered
        .filter(r => r[targetKey] !== undefined)
        .sort((a, b) => {
          const aScore = a[targetKey] as number;
          const bScore = b[targetKey] as number;
          return aScore - bScore; // Lower (more negative) = more dependent
        });
    } else if (searchQuery && !semanticMutation) {
      // Regular text search (only if no mutation filter)
      filtered = filtered.filter(r => r.cancer_type.toLowerCase().includes(searchQuery.toLowerCase()));
    }
    
    return filtered;
  })();

  const filteredTargetRankings = (searchQuery
    ? targetRankings.filter(t => t.Cancer?.toLowerCase().includes(searchQuery.toLowerCase()) || t.target?.toLowerCase().includes(searchQuery.toLowerCase()))
    : targetRankings).filter(t => t.Cancer !== 'Non-Cancerous');

  const filteredSL = searchQuery
    ? syntheticLethality.filter(sl => sl.mutation?.toLowerCase().includes(searchQuery.toLowerCase()) || sl.target?.toLowerCase().includes(searchQuery.toLowerCase()))
    : syntheticLethality;

  const filteredCellLines = (searchQuery
    ? cellLines.filter(cl => cl.cell_line?.toLowerCase().includes(searchQuery.toLowerCase()) || cl.cancer_type?.toLowerCase().includes(searchQuery.toLowerCase()))
    : cellLines).filter(cl => cl.cancer_type !== 'Non-Cancerous');

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent mx-auto"></div>
          <p className="mt-6 text-gray-600 text-lg">Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">StarX Therapeutics Dashboard</h1>
              <p className="text-gray-600 mt-1">Comprehensive cancer analysis and rankings</p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500">Last updated</div>
              <div className="text-sm font-medium text-gray-900">{new Date().toLocaleDateString()}</div>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Cancer Types</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.totalCancers}</p>
              </div>
              <div className="bg-blue-100 rounded-full p-3">
                <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Cell Lines</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.totalCellLines.toLocaleString()}</p>
              </div>
              <div className="bg-green-100 rounded-full p-3">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-purple-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">SL Hits</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.totalSLHits}</p>
              </div>
              <div className="bg-purple-100 rounded-full p-3">
                <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-orange-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Targets</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.totalTargets}</p>
              </div>
              <div className="bg-orange-100 rounded-full p-3">
                <svg className="w-8 h-8 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Chart Visualization */}
        <div className="mb-8">
          <TopCancersChart rankings={cancerRankings.filter(c => c.cancer_type !== 'Non-Cancerous')} />
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-md mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              {[
                { 
                  id: 'overview', 
                  label: 'Overview', 
                  icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
                },
                { 
                  id: 'cancer-rankings', 
                  label: 'Cancer Rankings', 
                  icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" /></svg>
                },
                { 
                  id: 'target-rankings', 
                  label: 'Target Rankings', 
                  icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
                },
                { 
                  id: 'synthetic-lethality', 
                  label: 'Synthetic Lethality', 
                  icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                },
                { 
                  id: 'cell-lines', 
                  label: 'Cell Lines', 
                  icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
                },
                { 
                  id: 'mutation-explorer', 
                  label: 'Mutation Explorer', 
                  icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
                },
                { 
                  id: 'upload', 
                  label: 'Upload Data', 
                  icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
                },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as TabType)}
                  className={`flex items-center px-6 py-4 text-sm font-semibold border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-700 hover:text-gray-900 hover:border-gray-300'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Search Bars */}
        <div className="mb-6 space-y-4">
          <div className="relative">
            <input
              type="text"
              placeholder="Search across all tables..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm text-gray-900 font-medium placeholder:text-gray-600"
            />
            <svg className="absolute left-4 top-3.5 h-5 w-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <SemanticSearch 
            onSearch={(query, target, mutation) => {
              setSearchQuery(query);
              setSemanticTarget(target || null);
              setSemanticMutation(mutation || null);
            }} 
          />
        </div>

        {/* Content */}
        <div className="space-y-6">
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <CancerRankingsCard 
                rankings={filteredCancerRankings.slice(0, 10)} 
                target={semanticTarget}
                mutation={semanticMutation}
              />
              <SyntheticLethalityCard 
                sl={filteredSL.filter(s => s.is_synthetic_lethal).slice(0, 10)} 
                target={semanticTarget}
              />
            </div>
          )}

          {activeTab === 'cancer-rankings' && (
            <CancerRankingsTable rankings={filteredCancerRankings} />
          )}

          {activeTab === 'target-rankings' && (
            <TargetRankingsTable rankings={filteredTargetRankings} />
          )}

          {activeTab === 'synthetic-lethality' && (
            <SyntheticLethalityTable sl={filteredSL} />
          )}

          {activeTab === 'cell-lines' && (
            <CellLinesTable cellLines={filteredCellLines} />
          )}

          {activeTab === 'mutation-explorer' && (
            <MutationContextExplorer />
          )}

          {activeTab === 'upload' && (
            <FileUpload />
          )}
        </div>
      </div>
    </div>
  );
}

// Component: Cancer Rankings Card (for overview)
function CancerRankingsCard({ rankings, target, mutation }: { rankings: CancerRanking[]; target?: string | null; mutation?: string | null }) {
  const subtitle = (() => {
    if (mutation && target) {
      return `Filtered: ${mutation} mutations, sorted by ${target} dependency`;
    } else if (mutation) {
      return `Filtered: ${mutation} mutations`;
    } else if (target) {
      return `Sorted by ${target} dependency`;
    }
    return 'Sorted by overall score';
  })();
  
  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden">
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4">
        <h2 className="text-xl font-bold text-white">Top Cancer Rankings</h2>
        <p className="text-blue-100 text-sm font-medium mt-1">{subtitle}</p>
      </div>
      <div className="p-6">
        <div className="space-y-3">
          {rankings.map((r) => (
            <div key={r.Rank} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center font-bold text-blue-600">
                  {r.Rank}
                </div>
                <div>
                  <div className="font-semibold text-gray-900">{r.cancer_type}</div>
                  <div className="text-sm font-medium text-gray-700">{r.n_cell_lines} cell lines</div>
                </div>
              </div>
              <div className="text-right">
                <div className="font-bold text-blue-600">{formatScore(r.overall_score)}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Component: Synthetic Lethality Card (for overview)
function SyntheticLethalityCard({ sl, target }: { sl: SyntheticLethality[]; target?: string | null }) {
  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden">
      <div className="bg-gradient-to-r from-purple-500 to-purple-600 px-6 py-4">
        <h2 className="text-xl font-bold text-white">Top Synthetic Lethality Hits</h2>
        <p className="text-purple-100 text-sm font-medium mt-1">
          {target ? `${target} interactions` : 'Most significant interactions'}
        </p>
      </div>
      <div className="p-6">
        <div className="space-y-3">
          {sl.map((s, idx) => (
            <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
              <div>
                <div className="font-semibold text-gray-900">{s.mutation} × {s.target}</div>
                <div className="text-sm font-medium text-gray-700">Effect: {formatScore(s.mean_diff)}</div>
              </div>
              <div className="text-right">
                <div className="text-xs font-medium text-gray-700">p = {formatPValue(s.p_value)}</div>
                <div className="text-xs text-purple-600 font-semibold mt-1">
                  {s.n_mutant} mutant / {s.n_wt} WT
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Component: Cancer Rankings Table
function CancerRankingsTable({ rankings }: { rankings: CancerRanking[] }) {
  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <h2 className="text-xl font-bold text-gray-900">Cancer Rankings</h2>
        <p className="text-sm font-medium text-gray-700 mt-1">Showing {rankings.length} cancer types</p>
      </div>
      <div className="overflow-x-auto -mx-4 sm:mx-0">
        <div className="inline-block min-w-full align-middle">
          <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-3 text-left text-xs font-semibold text-gray-700 uppercase sm:px-6">Rank</th>
                  <th className="px-3 py-3 text-left text-xs font-semibold text-gray-700 uppercase sm:px-6">Cancer Type</th>
                  <th className="px-3 py-3 text-left text-xs font-semibold text-gray-700 uppercase sm:px-6">Score</th>
                  <th className="px-3 py-3 text-left text-xs font-semibold text-gray-700 uppercase sm:px-6">Cell Lines</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {rankings.map((r) => {
                  return (
                    <tr key={r.Rank} className="hover:bg-gray-50">
                      <td className="px-3 py-4 whitespace-nowrap text-sm font-semibold text-gray-900 sm:px-6">{r.Rank}</td>
                      <td className="px-3 py-4 text-sm font-medium text-gray-900 sm:px-6">
                        <Link href={`/cancer/${encodeURIComponent(r.cancer_type)}`} className="text-blue-600 hover:text-blue-800 hover:underline font-semibold">
                          {r.cancer_type}
                        </Link>
                      </td>
                      <td className="px-3 py-4 whitespace-nowrap text-sm font-bold text-blue-600 sm:px-6">{formatScore(r.overall_score)}</td>
                      <td className="px-3 py-4 text-sm font-medium text-gray-700 sm:px-6">
                        <div className="max-w-xs truncate">{r.Cell_Lines?.split(',').slice(0, 2).join(', ')}...</div>
                        <div className="text-xs text-gray-600 font-medium">{r.n_cell_lines} lines</div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

// Component: Target Rankings Table
function TargetRankingsTable({ rankings }: { rankings: TargetRanking[] }) {
  const targets = ['STK17A', 'STK17B', 'MYLK4', 'TBK1', 'CLK4'];
  const [selectedTarget, setSelectedTarget] = useState<string>('STK17A');
  
  const filtered = rankings.filter(r => r.target === selectedTarget).slice(0, 20);

  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Target Rankings</h2>
            <p className="text-sm text-gray-600 mt-1">Individual target performance by cancer type</p>
          </div>
          <div className="flex space-x-2">
            {targets.map(t => (
              <button
                key={t}
                onClick={() => setSelectedTarget(t)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedTarget === t
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>
      </div>
      <div className="overflow-x-auto -mx-4 sm:mx-0">
        <div className="inline-block min-w-full align-middle">
          <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-3 text-left text-xs font-semibold text-gray-700 uppercase sm:px-6">Rank</th>
                  <th className="px-3 py-3 text-left text-xs font-semibold text-gray-700 uppercase sm:px-6">Cancer Type</th>
                  <th className="px-3 py-3 text-left text-xs font-semibold text-gray-700 uppercase sm:px-6">Target</th>
                  <th className="px-3 py-3 text-left text-xs font-semibold text-gray-700 uppercase sm:px-6">Mean Score</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filtered.map((r, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-3 py-4 whitespace-nowrap text-sm font-semibold text-gray-900 sm:px-6">{r.Rank}</td>
                    <td className="px-3 py-4 text-sm font-medium text-gray-900 sm:px-6">{r.Cancer}</td>
                    <td className="px-3 py-4 whitespace-nowrap sm:px-6">
                      <span className="px-2 py-1 text-xs font-semibold bg-blue-100 text-blue-800 rounded">{r.target}</span>
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm font-bold text-gray-900 sm:px-6">
                      {formatScore(r[`${r.target}_mean`] as number)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

// Component: Synthetic Lethality Table
function SyntheticLethalityTable({ sl }: { sl: SyntheticLethality[] }) {
  const trueHits = sl.filter(s => s.is_synthetic_lethal);

  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <h2 className="text-xl font-bold text-gray-900">Synthetic Lethality</h2>
        <p className="text-sm font-medium text-gray-700 mt-1">{trueHits.length} true hits out of {sl.length} combinations tested</p>
      </div>
      <div className="overflow-x-auto -mx-4 sm:mx-0">
        <div className="inline-block min-w-full align-middle">
          <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-3 text-left text-xs font-semibold text-gray-700 uppercase sm:px-6">Mutation</th>
                  <th className="px-3 py-3 text-left text-xs font-semibold text-gray-700 uppercase sm:px-6">Target</th>
                  <th className="px-3 py-3 text-left text-xs font-semibold text-gray-700 uppercase sm:px-6">Effect</th>
                  <th className="px-3 py-3 text-left text-xs font-semibold text-gray-700 uppercase sm:px-6">P-Value</th>
                  <th className="px-3 py-3 text-left text-xs font-semibold text-gray-700 uppercase sm:px-6">Samples</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {trueHits.map((s, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-3 py-4 whitespace-nowrap text-sm font-semibold text-gray-900 sm:px-6">{s.mutation}</td>
                    <td className="px-3 py-4 whitespace-nowrap sm:px-6">
                      <span className="px-2 py-1 text-xs font-semibold bg-purple-100 text-purple-800 rounded">{s.target}</span>
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm font-bold text-gray-900 sm:px-6">{formatScore(s.mean_diff)}</td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm font-medium text-gray-700 sm:px-6">{formatPValue(s.p_value)}</td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm font-medium text-gray-700 sm:px-6">
                      {s.n_mutant} mutant / {s.n_wt} WT
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

// Component: Cell Lines Table
function CellLinesTable({ cellLines }: { cellLines: CellLine[] }) {
  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <h2 className="text-xl font-bold text-gray-900">Cell Lines</h2>
        <p className="text-sm font-medium text-gray-700 mt-1">Showing {cellLines.length} cell lines</p>
      </div>
      <div className="overflow-x-auto -mx-4 sm:mx-0">
        <div className="inline-block min-w-full align-middle">
          <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-3 text-left text-xs font-semibold text-gray-700 uppercase sm:px-6">Cell Line</th>
                  <th className="px-3 py-3 text-left text-xs font-semibold text-gray-700 uppercase sm:px-6">Cancer Type</th>
                  <th className="px-3 py-3 text-left text-xs font-semibold text-gray-700 uppercase sm:px-6">Most Dependent Target</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {cellLines.map((cl, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-3 py-4 whitespace-nowrap text-sm font-semibold text-gray-900 sm:px-6">{cl.cell_line}</td>
                    <td className="px-3 py-4 text-sm font-medium text-gray-900 sm:px-6">{cl.cancer_type}</td>
                    <td className="px-3 py-4 whitespace-nowrap sm:px-6">
                      <span className="px-2 py-1 text-xs font-semibold bg-green-100 text-green-800 rounded">{cl.most_dependent_target}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

function formatScore(score: number) {
  return score?.toFixed(4) || 'N/A';
}

function formatPValue(p: number) {
  return p < 0.0001 ? p.toExponential(2) : p.toFixed(4);
}
