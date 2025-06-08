import React, { useState, useEffect } from 'react';
import { GraduationTrendChart } from './charts/GraduationTrendChart';
import { GenderBreakdownChart } from './charts/GenderBreakdownChart';
import { ProgramDistributionChart } from './charts/ProgramDistributionChart';
import { JobTitlesChart } from './charts/JobTitlesChart';
import { GeographicChart } from './charts/GeographicChart';
import * as Icons from 'lucide-react';

interface DashboardData {
  graduationTrend: Array<{ graduated_year: number; alumni_count: number }>;
  genderBreakdown: Array<{ gender: string; count: number }>;
  programDistribution: Array<{ program: string; count: number }>;
  jobTitles: Array<{ current_job_title: string; count: number }>;
  geographic: Array<{ country: string; count: number }>;
}

interface DashboardMetrics {
  total_alumni: number;
  active_programs: number;
  global_presence: number;
  employment_rate: number;
  total_graduation_years: number;
  total_graduates: number;
  current_year_grads: number;
  growth_rate: number;
}

interface MetricCard {
  title: string;
  value: string;
  change: string;
  changeType: 'positive' | 'negative' | 'neutral';
  icon: React.ReactNode;
  color: string;
}

export const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const baseUrl = 'http://localhost:8000/api/analytics';
      
      // Fetch both chart data and metrics
      const [chartDataResponse, metricsResponse] = await Promise.all([
        Promise.all([
          fetch(`${baseUrl}/graduation-cohort`),
          fetch(`${baseUrl}/gender-breakdown`),
          fetch(`${baseUrl}/program-distribution`),
          fetch(`${baseUrl}/top-job-titles`),
          fetch(`${baseUrl}/geographic-distribution`),
        ]),
        fetch(`${baseUrl}/dashboard-metrics`)
      ]);
      
      const [graduationTrend, genderBreakdown, programDistribution, jobTitles, geographic] = 
        await Promise.all(chartDataResponse.map(res => res.json()));
      
      const metricsData = await metricsResponse.json();

      // Transform the chart data
      const transformedData: DashboardData = {
        graduationTrend: graduationTrend.data.map((item: any) => ({
          graduated_year: item.year,
          alumni_count: item.count
        })),
        genderBreakdown: genderBreakdown.data.map((item: any) => ({
          gender: item.gender,
          count: item.count
        })),
        programDistribution: programDistribution.data.map((item: any) => ({
          program: item.program,
          count: item.count
        })),
        jobTitles: jobTitles.data.map((item: any) => ({
          current_job_title: item.job_title,
          count: item.count
        })),
        geographic: geographic.data.map((item: any) => ({
          country: item.country,
          count: item.count
        }))
      };
      
      setData(transformedData);
      setMetrics(metricsData.data);
    } catch (err) {
      setError('Failed to fetch dashboard data');
      console.error('Dashboard data fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Calculate metrics from real data
  const getMetrics = (): MetricCard[] => {
    if (!metrics) return [];

    const metricCards: MetricCard[] = [
      {
        title: 'Total Alumni',
        value: metrics.total_alumni.toLocaleString(),
        change: `${metrics.growth_rate >= 0 ? '+' : ''}${metrics.growth_rate}% from last year`,
        changeType: metrics.growth_rate >= 0 ? 'positive' : 'negative',
        icon: <Icons.Users className="w-6 h-6" />,
        color: 'from-blue-500 to-blue-600'
      },
      {
        title: 'Active Programs',
        value: metrics.active_programs.toString(),
        change: `${metrics.active_programs > 0 ? '+' : ''}${metrics.active_programs} active programs`,
        changeType: 'positive',
        icon: <Icons.GraduationCap className="w-6 h-6" />,
        color: 'from-purple-500 to-purple-600'
      },
      {
        title: 'Global Presence',
        value: `${metrics.global_presence} Countries`,
        change: `${metrics.global_presence > 0 ? '+' : ''}${metrics.global_presence} countries`,
        changeType: 'positive',
        icon: <Icons.MapPin className="w-6 h-6" />,
        color: 'from-teal-500 to-teal-600'
      },
      {
        title: 'Employment Rate',
        value: `${metrics.employment_rate}%`,
        change: `${metrics.employment_rate > 0 ? '+' : ''}${metrics.employment_rate}% employed`,
        changeType: 'positive',
        icon: <Icons.Briefcase className="w-6 h-6" />,
        color: 'from-green-500 to-green-600'
      },
      {
        title: '2024 Graduates',
        value: metrics.current_year_grads.toLocaleString(),
        change: `${metrics.growth_rate >= 0 ? '+' : ''}${metrics.growth_rate}% vs 2023`,
        changeType: metrics.growth_rate >= 0 ? 'positive' : 'negative',
        icon: <Icons.TrendingUp className="w-6 h-6" />,
        color: 'from-orange-500 to-orange-600'
      }
    ];

    return metricCards;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex items-center space-x-3">
          <Icons.RefreshCw className="w-6 h-6 animate-spin text-blue-600" />
          <span className="text-lg font-medium text-gray-700">Loading dashboard...</span>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-red-800 font-medium">Error Loading Dashboard</h3>
            <p className="text-red-600 mt-1">{error || 'Unknown error occurred'}</p>
          </div>
          <button
            onClick={fetchDashboardData}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const metricCards = getMetrics();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Alumni Dashboard</h1>
          <p className="text-gray-600 mt-2">Comprehensive insights into our alumni network</p>
        </div>
        <button
          onClick={fetchDashboardData}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Icons.RefreshCw className="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        {metricCards.map((metric, index) => (
          <div
            key={index}
            className={`bg-white rounded-xl shadow-sm p-6 border border-gray-100 hover:shadow-md transition-shadow`}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-500 text-sm font-medium">{metric.title}</h3>
              <div className={`p-2 rounded-lg bg-gradient-to-br ${metric.color}`}>
                {metric.icon}
              </div>
            </div>
            <div className="space-y-1">
              <p className="text-2xl font-semibold text-gray-900">{metric.value}</p>
              <div className="flex items-center space-x-2">
                <span
                  className={`text-sm font-medium ${
                    metric.changeType === 'positive'
                      ? 'text-green-600'
                      : metric.changeType === 'negative'
                      ? 'text-red-600'
                      : 'text-gray-600'
                  }`}
                >
                  {metric.change}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <GraduationTrendChart data={data.graduationTrend} />
        </div>
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <GenderBreakdownChart data={data.genderBreakdown} />
        </div>
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <ProgramDistributionChart data={data.programDistribution} />
        </div>
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <JobTitlesChart data={data.jobTitles} />
        </div>
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 lg:col-span-2">
          <GeographicChart data={data.geographic} />
        </div>
      </div>
    </div>
  );
};