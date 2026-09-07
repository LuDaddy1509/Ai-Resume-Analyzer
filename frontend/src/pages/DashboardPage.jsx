import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText,
  BarChart3,
  TrendingUp,
  Target,
  Clock,
  Upload,
  Search,
  History,
  RefreshCw,
  AlertCircle,
} from 'lucide-react';
import { dashboardAPI, resumeAPI } from '../services/api';
import PageLoader from '../components/PageLoader';
import EmptyState from '../components/EmptyState';
import ScoreBadge from '../components/ScoreBadge';

export default function DashboardPage() {
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [recentHistory, setRecentHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [summaryData, historyData] = await Promise.all([
        dashboardAPI.getSummary().catch(() => null),
        resumeAPI.getHistory().catch(() => []),
      ]);
      setSummary(summaryData);
      setRecentHistory(historyData.slice(0, 5));
    } catch {
      setError('The dashboard is available, but saved data could not be loaded. Check the server connection and try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (loading) return <PageLoader />;

  const totalResumes = summary?.total_resumes || recentHistory.length || 0;
  const avgScore = summary?.avg_match_score || 0;
  const hasData = totalResumes > 0;

  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-header__title">Dashboard</h1>
        <p className="page-header__subtitle">Welcome back! Here&apos;s an overview of your CV analysis activity.</p>
      </div>

      {/* Error state */}
      {error && (
        <div className="alert alert-warning mb-6" role="alert">
          <AlertCircle size={20} />
          <div style={{ flex: 1 }}>
            <div className="font-semibold">Data Loading Issue</div>
            <div className="text-sm mt-2">{error}</div>
          </div>
          <button className="btn btn-sm btn-secondary" onClick={loadData}>
            <RefreshCw size={14} />
            Retry
          </button>
        </div>
      )}

      {/* Quick Actions */}
      <div className="grid-4 mb-8">
        <button className="stat-card card-clickable" onClick={() => navigate('/resumes/import')} style={{ border: 'none', cursor: 'pointer', textAlign: 'left' }}>
          <div className="stat-card__icon" style={{ background: 'var(--color-primary-50)', color: 'var(--color-primary)' }}>
            <Upload size={24} />
          </div>
          <div className="font-semibold">Import CV</div>
          <div className="text-sm text-muted mt-2">Upload a new CV</div>
        </button>
        <button className="stat-card card-clickable" onClick={() => navigate('/analyze')} style={{ border: 'none', cursor: 'pointer', textAlign: 'left' }}>
          <div className="stat-card__icon" style={{ background: 'var(--color-accent-light)', color: 'var(--color-accent)' }}>
            <Search size={24} />
          </div>
          <div className="font-semibold">Analyze CV</div>
          <div className="text-sm text-muted mt-2">Run AI analysis</div>
        </button>
        <button className="stat-card card-clickable" onClick={() => navigate('/analysis-history')} style={{ border: 'none', cursor: 'pointer', textAlign: 'left' }}>
          <div className="stat-card__icon" style={{ background: 'var(--color-warning-light)', color: 'var(--color-warning)' }}>
            <History size={24} />
          </div>
          <div className="font-semibold">Analysis History</div>
          <div className="text-sm text-muted mt-2">View analysis history</div>
        </button>
      </div>

      {/* Summary Cards */}
      {hasData && (
        <div className="grid-4 mb-8">
          <div className="stat-card">
            <div className="stat-card__icon" style={{ background: 'var(--color-primary-50)', color: 'var(--color-primary)' }}>
              <FileText size={22} />
            </div>
            <div className="stat-card__value">{totalResumes}</div>
            <div className="stat-card__label">Total CVs Analyzed</div>
          </div>
          <div className="stat-card">
            <div className="stat-card__icon" style={{ background: 'var(--color-success-light)', color: 'var(--color-success)' }}>
              <TrendingUp size={22} />
            </div>
            <div className="stat-card__value">{avgScore.toFixed(0)}%</div>
            <div className="stat-card__label">Average Score</div>
          </div>
          <div className="stat-card">
            <div className="stat-card__icon" style={{ background: 'var(--color-info-light)', color: 'var(--color-info)' }}>
              <BarChart3 size={22} />
            </div>
            <div className="stat-card__value">{totalResumes}</div>
            <div className="stat-card__label">Completed Analyses</div>
          </div>
          <div className="stat-card">
            <div className="stat-card__icon" style={{ background: 'var(--color-accent-light)', color: 'var(--color-accent)' }}>
              <Target size={22} />
            </div>
            <div className="stat-card__value">
              {recentHistory[0]?.match_score ?? '—'}%
            </div>
            <div className="stat-card__label">Latest Score</div>
          </div>
        </div>
      )}

      {/* Empty state */}
      {!hasData && !error && (
        <EmptyState
          icon={FileText}
          title="No CVs saved yet"
          message="Import your first CV to begin AI analysis. Upload a PDF or DOCX file to get started."
          action={
            <button className="btn btn-primary" onClick={() => navigate('/resumes/import')}>
              <Upload size={18} />
              Import CV / Resume
            </button>
          }
        />
      )}

      {/* Recent Analysis Results */}
      {recentHistory.length > 0 && (
        <div className="card">
          <div className="card-header flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Clock size={18} />
              Recent Analysis Results
            </span>
            <button className="btn btn-ghost btn-sm" onClick={() => navigate('/analysis-history')}>
              View All
            </button>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Candidate</th>
                  <th>Filename</th>
                  <th>Score</th>
                  <th>Date</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {recentHistory.map((item) => (
                  <tr key={item.id}>
                    <td className="font-medium">{item.full_name || '—'}</td>
                    <td className="text-secondary">{item.filename}</td>
                    <td>
                      <ScoreBadge score={item.match_score} />
                    </td>
                    <td className="text-muted text-sm">
                      {item.created_at ? new Date(item.created_at).toLocaleDateString() : '—'}
                    </td>
                    <td>
                      <button className="btn btn-ghost btn-sm" onClick={() => navigate('/analysis-history')}>
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
