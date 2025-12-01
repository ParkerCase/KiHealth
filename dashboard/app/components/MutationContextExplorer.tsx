'use client';

import { useState, useEffect } from 'react';

interface SyntheticLethality {
  mutation: string;
  target: string;
  is_synthetic_lethal: boolean;
  p_value: number;
  mean_diff: number;
  n_mutant: number;
  n_wt: number;
  mutant_mean: number;
  wt_mean: number;
  [key: string]: any;
}

export default function MutationContextExplorer() {
  const [mutations, setMutations] = useState<string[]>([]);
  const [selectedMutation, setSelectedMutation] = useState<string>('');
  const [slData, setSlData] = useState<SyntheticLethality[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchMutations();
  }, []);

  useEffect(() => {
    if (selectedMutation) {
      fetchMutationData(selectedMutation);
    }
  }, [selectedMutation]);

  const fetchMutations = async () => {
    try {
      const response = await fetch('/api/synthetic-lethality');
      if (response.ok) {
        const data = await response.json();
        const uniqueMutations = [...new Set(data.map((sl: SyntheticLethality) => sl.mutation))].sort();
        setMutations(uniqueMutations);
      }
    } catch (error) {
      console.error('Error fetching mutations:', error);
    }
  };

  const fetchMutationData = async (mutation: string) => {
    setLoading(true);
    try {
      const response = await fetch('/api/synthetic-lethality');
      if (response.ok) {
        const data = await response.json();
        const filtered = data.filter((sl: SyntheticLethality) => 
          sl.mutation === mutation && sl.is_synthetic_lethal
        );
        setSlData(filtered);
      }
    } catch (error) {
      console.error('Error fetching mutation data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden">
      <div className="bg-gradient-to-r from-purple-500 to-purple-600 px-6 py-4">
        <h2 className="text-xl font-bold text-white">Mutation Context Explorer</h2>
        <p className="text-purple-100 text-sm mt-1">Explore synthetic lethality by mutation</p>
      </div>
      <div className="p-6">
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Mutation
          </label>
          <select
            value={selectedMutation}
            onChange={(e) => setSelectedMutation(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="">Choose a mutation...</option>
            {mutations.map(m => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>

        {loading && (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
          </div>
        )}

        {!loading && selectedMutation && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Synthetic Lethality Hits for {selectedMutation}
            </h3>
            {slData.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No synthetic lethality hits found for this mutation.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Target</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Effect</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">P-Value</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Mutant Mean</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">WT Mean</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Samples</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {slData.map((sl, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="px-4 py-3 whitespace-nowrap">
                          <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-800 rounded">
                            {sl.target}
                          </span>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                          {sl.mean_diff.toFixed(4)}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                          {sl.p_value < 0.0001 ? sl.p_value.toExponential(2) : sl.p_value.toFixed(4)}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                          {sl.mutant_mean?.toFixed(4) || 'N/A'}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                          {sl.wt_mean?.toFixed(4) || 'N/A'}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                          {sl.n_mutant} / {sl.n_wt}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

