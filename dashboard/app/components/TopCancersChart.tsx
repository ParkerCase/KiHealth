'use client';

import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface CancerRanking {
  Rank: number;
  cancer_type: string;
  overall_score: number;
}

export default function TopCancersChart({ rankings }: { rankings: CancerRanking[] }) {
  const top10 = rankings.slice(0, 10);

  const data = {
    labels: top10.map(r => r.cancer_type),
    datasets: [
      {
        label: 'Overall Score',
        data: top10.map(r => r.overall_score),
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            return `Score: ${context.parsed.y.toFixed(4)}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 0.6,
        ticks: {
          precision: 3,
        },
      },
      x: {
        ticks: {
          maxRotation: 45,
          minRotation: 45,
          font: {
            size: 10,
          },
        },
      },
    },
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-gray-900">Top 10 Cancer Types</h2>
        <p className="text-sm text-gray-600 mt-1">Overall score comparison</p>
      </div>
      <div className="h-64">
        <Bar data={data} options={options} />
      </div>
    </div>
  );
}

