import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

export default function DashboardPage() {
  const [dateRange, setDateRange] = useState('30d');
  const [customDateFrom, setCustomDateFrom] = useState('');
  const [customDateTo, setCustomDateTo] = useState('');
  const [scoreType, setScoreType] = useState('match');

  const [summary, setSummary] = useState(null);
  const [scoreDistribution, setScoreDistribution] = useState(null);
  const [topSkills, setTopSkills] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, [dateRange, scoreType, customDateFrom, customDateTo]);

  const getDateParams = () => {
    if (dateRange === 'custom') {
      return {
        date_from: customDateFrom,
        date_to: customDateTo
      };
    }

    const now = new Date();
    let fromDate = new Date();

    switch (dateRange) {
      case '7d':
        fromDate.setDate(now.getDate() - 7);
        break;
      case '30d':
        fromDate.setDate(now.getDate() - 30);
        break;
      case '90d':
        fromDate.setDate(now.getDate() - 90);
        break;
      default:
        return {};
    }

    return {
      date_from: fromDate.toISOString().split('T')[0],
      date_to: now.toISOString().split('T')[0]
    };
  };

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);

    try {
      const dateParams = getDateParams();

      const [summaryRes, distributionRes, skillsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/dashboard/summary`, { params: dateParams }),
        axios.get(`${API_BASE_URL}/api/dashboard/score-distribution`, {
          params: { ...dateParams, score_type: scoreType }
        }),
        axios.get(`${API_BASE_URL}/api/dashboard/top-skills`, {
          params: { ...dateParams, limit: 10 }
        })
      ]);

      setSummary(summaryRes.data);
      setScoreDistribution(distributionRes.data);
      setTopSkills(skillsRes.data);
    } catch (err) {
      console.error('Dashboard error:', err);
      setError('Không thể tải dữ liệu dashboard');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Đang tải...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        {error}
      </div>
    );
  }

  return (
    <div className="container-fluid">
      <h2 className="fw-bold mb-4">Dashboard</h2>

      {/* Filters */}
      <div className="card shadow mb-4">
        <div className="card-body">
          <div className="row">
            <div className="col-md-4">
              <label className="form-label fw-bold">Khoảng thời gian</label>
              <select
                className="form-select"
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
              >
                <option value="7d">7 ngày qua</option>
                <option value="30d">30 ngày qua</option>
                <option value="90d">90 ngày qua</option>
                <option value="custom">Tùy chỉnh</option>
              </select>
            </div>

            {dateRange === 'custom' && (
              <>
                <div className="col-md-3">
                  <label className="form-label fw-bold">Từ ngày</label>
                  <input
                    type="date"
                    className="form-control"
                    value={customDateFrom}
                    onChange={(e) => setCustomDateFrom(e.target.value)}
                  />
                </div>
                <div className="col-md-3">
                  <label className="form-label fw-bold">Đến ngày</label>
                  <input
                    type="date"
                    className="form-control"
                    value={customDateTo}
                    onChange={(e) => setCustomDateTo(e.target.value)}
                  />
                </div>
              </>
            )}

            <div className="col-md-4">
              <label className="form-label fw-bold">Loại điểm</label>
              <select
                className="form-select"
                value={scoreType}
                onChange={(e) => setScoreType(e.target.value)}
              >
                <option value="match">Match Score</option>
                <option value="ats">ATS Score</option>
                <option value="overall">Overall Score</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="row mb-4">
        <div className="col-md-6 mb-3">
          <div className="card shadow h-100">
            <div className="card-body">
              <h6 className="card-subtitle mb-2 text-muted">Tổng số CV đã phân tích</h6>
              <h2 className="card-title fw-bold text-primary">
                {summary?.total_resumes || 0}
              </h2>
            </div>
          </div>
        </div>

        <div className="col-md-6 mb-3">
          <div className="card shadow h-100">
            <div className="card-body">
              <h6 className="card-subtitle mb-2 text-muted">Điểm trung bình</h6>
              <h2 className="card-title fw-bold text-success">
                {summary?.avg_match_score?.toFixed(1) || 0}%
              </h2>
            </div>
          </div>
        </div>
      </div>

      {/* Score Distribution Chart */}
      <div className="card shadow mb-4">
        <div className="card-header bg-primary text-white fw-bold">
          Phân bố điểm số
        </div>
        <div className="card-body">
          {scoreDistribution?.buckets && scoreDistribution.buckets.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={scoreDistribution.buckets}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="label" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#3498db" name="Số lượng CV" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-muted text-center py-5">Chưa có dữ liệu</p>
          )}
        </div>
      </div>

      {/* Top Skills Chart */}
      <div className="card shadow mb-4">
        <div className="card-header bg-success text-white fw-bold">
          Top 10 kỹ năng phổ biến
        </div>
        <div className="card-body">
          {topSkills && topSkills.length > 0 ? (
            <ResponsiveContainer width="100%" height={400}>
              <BarChart
                data={topSkills}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="skill" type="category" />
                <Tooltip />
                <Legend />
                <Bar dataKey="resume_count" fill="#27ae60" name="Số CV" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-muted text-center py-5">Chưa có dữ liệu</p>
          )}
        </div>
      </div>
    </div>
  );
}
