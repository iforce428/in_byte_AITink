import React, { useState, useEffect } from 'react';
import { GraduationTrendChart } from './charts/GraduationTrendChart';
import { GenderBreakdownChart } from './charts/GenderBreakdownChart';
import { ProgramDistributionChart } from './charts/ProgramDistributionChart';
import { JobTitlesChart } from './charts/JobTitlesChart';
import { GeographicChart } from './charts/GeographicChart';
import { RefreshCw, Users, GraduationCap, MapPin, Briefcase, TrendingUp } from 'lucide-react';

interface DashboardData {
  graduationTrend: Array<{ graduated_year: number; alumni_count: number }>;
  genderBreakdown: Array<{ gender: string; count: number }>;
  programDistribution: Array<{ program: string; count: number }>;
  jobTitles: Array<{ current_job_title: string; count: number }>;
  geographic: Array<{ country: string; count: number }>;
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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // In a real implementation, you would make POST requests to your Supabase backend
      // For demo purposes, we'll use mock data
      
      // Example of how the actual API calls would look:
      /*
      const responses = await Promise.all([
        fetch('/api/graduation-trend', { method: 'POST' }),
        fetch('/api/gender-breakdown', { method: 'POST' }),
        fetch('/api/program-distribution', { method: 'POST' }),
        fetch('/api/job-titles', { method: 'POST' }),
        fetch('/api/geographic', { method: 'POST' }),
      ]);
      
      const [graduationTrend, genderBreakdown, programDistribution, jobTitles, geographic] = 
        await Promise.all(responses.map(res => res.json()));
      */

      // Mock data for demonstration
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API delay
      
      const mockData: DashboardData = {
        graduationTrend: [
          { graduated_year: 2018, alumni_count: 245 },
          { graduated_year: 2019, alumni_count: 312 },
          { graduated_year: 2020, alumni_count: 189 },
          { graduated_year: 2021, alumni_count: 278 },
          { graduated_year: 2022, alumni_count: 356 },
          { graduated_year: 2023, alumni_count: 423 },
          { graduated_year: 2024, alumni_count: 198 },
        ],
        genderBreakdown: [
          { gender: 'Female', count: 1287 },
          { gender: 'Male', count: 1043 },
          { gender: 'Non-binary', count: 89 },
          { gender: 'Prefer not to say', count: 45 },
        ],
        programDistribution: [
          { program: 'Computer Science', count: 567 },
          { program: 'Business Administration', count: 423 },
          { program: 'Engineering', count: 389 },
          { program: 'Data Science', count: 234 },
          { program: 'Digital Marketing', count: 198 },
          { program: 'Design', count: 167 },
        ],
        jobTitles: [
          { current_job_title: 'Software Engineer', count: 234 },
          { current_job_title: 'Product Manager', count: 167 },
          { current_job_title: 'Data Analyst', count: 143 },
          { current_job_title: 'UX Designer', count: 98 },
          { current_job_title: 'Business Analyst', count: 87 },
          { current_job_title: 'Marketing Manager', count: 76 },
          { current_job_title: 'DevOps Engineer', count: 65 },
          { current_job_title: 'Sales Representative', count: 54 },
        ],
        geographic: [
          { country: 'United States', count: 678 },
          { country: 'Canada', count: 234 },
          { country: 'United Kingdom', count: 189 },
          { country: 'Germany', count: 143 },
          { country: 'Australia', count: 98 },
          { country: 'Netherlands', count: 76 },
          { country: 'Singapore', count: 65 },
          { country: 'France', count: 54 },
        ],
      };
      
      setData(mockData);
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

  // Calculate metrics from data
  const getMetrics = (): MetricCard[] => {
    if (!data) return [];

    const totalAlumni = data.genderBreakdown.reduce((sum, item) => sum + item.count, 0);
    const totalCountries = data.geographic.length;
    const totalPrograms = data.programDistribution.length;
    const currentYearGrads = data.graduationTrend.find(item => item.graduated_year === 2024)?.alumni_count || 0;
    const lastYearGrads = data.graduationTrend.find(item => item.graduated_year === 2023)?.alumni_count || 0;
    const growthRate = lastYearGrads > 0 ? ((currentYearGrads - lastYearGrads) / lastYearGrads * 100) : 0;

    return [
      {
        title: 'Total Alumni',
        value: totalAlumni.toLocaleString(),
        change: '+12.5% from last year',
        changeType: 'positive',
        icon: <Users className="w-6 h-6" />,
        color: 'from-blue-500 to-blue-600'
      },
      {
        title: 'Active Programs',
        value: totalPrograms.toString(),
        change: '+2 new programs',
        changeType: 'positive',
        icon: <GraduationCap className="w-6 h-6" />,
        color: 'from-purple-500 to-purple-600'
      },
      {
        title: 'Global Presence',
        value: `${totalCountries} Countries`,
        change: '+3 new countries',
        changeType: 'positive',
        icon: <MapPin className="w-6 h-6" />,
        color: 'from-teal-500 to-teal-600'
      },
      {
        title: 'Employment Rate',
        value: '94.2%',
        change: '+2.1% improvement',
        changeType: 'positive',
        icon: <Briefcase className="w-6 h-6" />,
        color: 'from-green-500 to-green-600'
      },
      {
        title: '2024 Graduates',
        value: currentYearGrads.toLocaleString(),
        change: `${growthRate >= 0 ? '+' : ''}${growthRate.toFixed(1)}% vs 2023`,
        changeType: growthRate >= 0 ? 'positive' : 'negative',
        icon: <TrendingUp className="w-6 h-6" />,
        color: 'from-orange-500 to-orange-600'
      }
    ];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex items-center space-x-3">
          <RefreshCw className="w-6 h-6 animate-spin text-blue-600" />
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

  const metrics = getMetrics();

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
          <RefreshCw className="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        {metrics.map((metric, index) => (
          <div
            key={index}
            className="bg-white rounded-xl shadow-lg border border-gray-100 p-6 hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`p-3 rounded-xl bg-gradient-to-r ${metric.color} text-white shadow-lg`}>
                {metric.icon}
              </div>
            </div>
            
            <div className="space-y-2">
              <h3 className="text-sm font-medium text-gray-600 uppercase tracking-wide">
                {metric.title}
              </h3>
              <p className="text-2xl font-bold text-gray-900">
                {metric.value}
              </p>
              <div className="flex items-center space-x-1">
                <span className={`text-sm font-medium ${
                  metric.changeType === 'positive' 
                    ? 'text-green-600' 
                    : metric.changeType === 'negative' 
                    ? 'text-red-600' 
                    : 'text-gray-600'
                }`}>
                  {metric.change}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Graduation Trend */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6 hover:shadow-xl transition-shadow">
          <GraduationTrendChart data={data.graduationTrend} />
        </div>

        {/* Gender Breakdown */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6 hover:shadow-xl transition-shadow">
          <GenderBreakdownChart data={data.genderBreakdown} />
        </div>

        {/* Program Distribution */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6 hover:shadow-xl transition-shadow">
          <ProgramDistributionChart data={data.programDistribution} />
        </div>

        {/* Job Titles */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6 hover:shadow-xl transition-shadow">
          <JobTitlesChart data={data.jobTitles} />
        </div>
      </div>

      {/* Geographic Chart - Full Width */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6 hover:shadow-xl transition-shadow">
        <GeographicChart data={data.geographic} />
      </div>
    </div>
  );
};