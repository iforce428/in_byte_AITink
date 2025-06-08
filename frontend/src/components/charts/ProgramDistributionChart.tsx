import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface ProgramDistributionData {
  program: string;
  count: number;
}

interface ProgramDistributionChartProps {
  data: ProgramDistributionData[];
}

export const ProgramDistributionChart: React.FC<ProgramDistributionChartProps> = ({ data }) => {
  const chartData = {
    labels: data.map(item => item.program),
    datasets: [
      {
        label: 'Alumni Count',
        data: data.map(item => item.count),
        backgroundColor: 'rgba(139, 92, 246, 0.8)',
        borderColor: '#8B5CF6',
        borderWidth: 1,
        borderRadius: 4,
        borderSkipped: false,
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
        display: true,
        text: 'Program Distribution',
        font: {
          size: 16,
          weight: '600',
        },
        color: '#111827',
        padding: 20,
      },
      tooltip: {
        backgroundColor: 'rgba(17, 24, 39, 0.9)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: '#8B5CF6',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(156, 163, 175, 0.2)',
        },
        ticks: {
          font: {
            size: 11,
          },
          color: '#6B7280',
        },
      },
      x: {
        grid: {
          display: false,
        },
        ticks: {
          font: {
            size: 11,
          },
          color: '#6B7280',
          maxRotation: 45,
        },
      },
    },
  };

  return (
    <div className="h-80">
      <Bar data={chartData} options={options} />
    </div>
  );
};