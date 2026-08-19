import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { History, Search, Calendar, FileText } from 'lucide-react';
import { resumeAPI } from '../services/api';
import PageLoader from '../components/PageLoader';
import EmptyState from '../components/EmptyState';
import ScoreBadge from '../components/ScoreBadge';

export default function AnalysisHistoryPage() {
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('newest');

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await resumeAPI.getHistory();
      setHistory(data);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  const filtered = history
    .filter((h) => {
      const q = searchQuery.toLowerCase();
      return !q || h.full_name?.toLowerCase().includes(q) || h.filename?.toLowerCase().includes(q);
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'oldest':
          return new Date(a.created_at) - new Date(b.created_at);
        case 'score-high':
          return (b.match_score || 0) - (a.match_score || 0);
        case 'score-low':
          return (a.match_score || 0) - (b.match_score || 0);
        default: // newest
          return new Date(b.created_at) - new Date(a.created_at);
      }
    });

  if (loading) return <PageLoader />;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-header__title">Analysis History</h1>
        <p className="page-header__subtitle">{history.length} analysis result{history.length !== 1 ? 's' : ''}</p>
      </div>

      {history.length === 0 ? (
        <EmptyState
          icon={History}
          title="No analysis history"
          message="Your analysis results will appear here after you analyze a CV."
          action={
            <button className="btn btn-primary" onClick={() => navigate('/analyze')}>
              <Search size={18} />
              Analyze CV
            </button>
          }
        />
      ) : (
        <>
          {/* Filters */}
          <div className="flex gap-4 mb-6 flex-wrap">
            <div className="search-input-wrapper" style={{ flex: 1, minWidth: 200 }}>
              <Search size={18} className="search-icon" />
              <input
                className="search-input"
                placeholder="Search by name or filename..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <select
              className="form-select"
              style={{ width: 'auto', minWidth: 160 }}
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="newest">Newest first</option>
              <option value="oldest">Oldest first</option>
              <option value="score-high">Highest score</option>
              <option value="score-low">Lowest score</option>
            </select>
          </div>

          {/* Results table */}
          <div className="card">
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Candidate</th>
                    <th>Filename</th>
                    <th>Score</th>
                    <th>Date</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((item) => (
                    <tr key={item.id}>
                      <td>
                        <div className="flex items-center gap-2">
                          <FileText size={16} color="var(--color-primary)" />
                          <span className="font-medium">{item.full_name || '—'}</span>
                        </div>
                      </td>
                      <td className="text-secondary text-sm">{item.filename}</td>
                      <td>
                        <ScoreBadge score={item.match_score} />
                      </td>
                      <td>
                        <span className="flex items-center gap-1 text-muted text-sm">
                          <Calendar size={14} />
                          {item.created_at ? new Date(item.created_at).toLocaleDateString() : '—'}
                        </span>
                      </td>
                      <td>
                        <button className="btn btn-ghost btn-sm" onClick={() => navigate('/analyze')}>
                          Reanalyze
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {filtered.length === 0 && history.length > 0 && (
            <div className="text-center mt-6 text-muted">
              No results match your search.
            </div>
          )}
        </>
      )}
    </div>
  );
}
