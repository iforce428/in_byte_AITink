import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface GraduationTrendData {
  graduated_year: number;
  alumni_count: number;
}

interface GraduationTrendChartProps {
  data: GraduationTrendData[];
}

export const GraduationTrendChart: React.FC<GraduationTrendChartProps> = ({ data = [] }) => {
  // Ensure data is valid and sorted by year
  const validData = data
    .filter(item => item && typeof item.graduated_year === 'number' && typeof item.alumni_count === 'number')
    .sort((a, b) => a.graduated_year - b.graduated_year);

  const chartData = {
    labels: validData.map(item => item.graduated_year.toString()),
    datasets: [
      {
        label: 'Alumni Count',
        data: validData.map(item => item.alumni_count),
        borderColor: '#3B82F6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true,
        pointBackgroundColor: '#3B82F6',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 6,
        pointHoverRadius: 8,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          font: {
            size: 12,
            weight: 'normal' as const,
          },
          color: '#374151',
        },
      },
      title: {
        display: true,
        text: 'Graduation Cohort Trend',
        font: {
          size: 16,
          weight: 'bold' as const,
        },
        color: '#111827',
        padding: 20,
      },
      tooltip: {
        backgroundColor: 'rgba(17, 24, 39, 0.9)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: '#3B82F6',
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
            weight: 'normal' as const,
          },
          color: '#6B7280',
        },
      },
      x: {
        grid: {
          color: 'rgba(156, 163, 175, 0.2)',
        },
        ticks: {
          font: {
            size: 11,
            weight: 'normal' as const,
          },
          color: '#6B7280',
        },
      },
    },
  };

  return (
    <div className="h-80">
      <Line data={chartData} options={options} />
    </div>
  );
};