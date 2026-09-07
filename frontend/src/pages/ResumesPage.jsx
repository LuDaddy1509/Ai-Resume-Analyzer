import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Search, Upload, Calendar } from 'lucide-react';
import { resumeAPI } from '../services/api';
import PageLoader from '../components/PageLoader';
import EmptyState from '../components/EmptyState';
import ScoreBadge from '../components/ScoreBadge';
import ConfirmDialog from '../components/ConfirmDialog';

export default function ResumesPage() {
  const navigate = useNavigate();
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [deleteId, setDeleteId] = useState(null);

  useEffect(() => {
    loadResumes();
  }, []);

  const loadResumes = async () => {
    setLoading(true);
    try {
      const data = await resumeAPI.getHistory();
      setResumes(data);
    } catch (err) {
      console.error('Failed to load resumes:', err);
    } finally {
      setLoading(false);
    }
  };

  const filtered = resumes.filter((r) => {
    const q = searchQuery.toLowerCase();
    return (
      !q ||
      r.full_name?.toLowerCase().includes(q) ||
      r.filename?.toLowerCase().includes(q)
    );
  });

  if (loading) return <PageLoader />;

  return (
    <div>
      <div className="page-header">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h1 className="page-header__title">My CVs / Resumes</h1>
            <p className="page-header__subtitle">{resumes.length} document{resumes.length !== 1 ? 's' : ''} saved</p>
          </div>
          <button className="btn btn-primary" onClick={() => navigate('/resumes/import')}>
            <Upload size={18} />
            Import CV
          </button>
        </div>
      </div>

      {/* Search */}
      {resumes.length > 0 && (
        <div className="search-input-wrapper mb-6">
          <Search size={18} className="search-icon" />
          <input
            className="search-input"
            placeholder="Search by name or filename..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      )}

      {/* Empty state */}
      {resumes.length === 0 && (
        <EmptyState
          icon={FileText}
          title="No CVs saved yet"
          message="Import your first CV to get started with AI analysis."
          action={
            <button className="btn btn-primary" onClick={() => navigate('/resumes/import')}>
              <Upload size={18} />
              Import CV / Resume
            </button>
          }
        />
      )}

      {/* Results */}
      {filtered.length > 0 && (
        <div style={{ display: 'grid', gap: 'var(--space-4)' }}>
          {filtered.map((resume) => (
            <div key={resume.id} className="card" style={{ padding: 'var(--space-5)' }}>
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div className="flex items-center gap-4" style={{ minWidth: 0 }}>
                  <div style={{
                    width: 44, height: 44, borderRadius: 'var(--radius-md)',
                    background: 'var(--color-primary-50)', color: 'var(--color-primary)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0
                  }}>
                    <FileText size={22} />
                  </div>
                  <div style={{ minWidth: 0 }}>
                    <div className="font-semibold" style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {resume.full_name || 'Unknown'}
                    </div>
                    <div className="text-sm text-muted" style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {resume.filename}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  {resume.match_score != null && (
                    <ScoreBadge score={resume.match_score} />
                  )}
                  {resume.skills && JSON.parse(typeof resume.skills === 'string' ? resume.skills : '[]').length > 0 && (
                    <div className="text-sm text-muted" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
                      {JSON.parse(typeof resume.skills === 'string' ? resume.skills : '[]').length} skills
                    </div>
                  )}
                  <div className="text-sm text-muted flex items-center gap-1">
                    <Calendar size={14} />
                    {resume.created_at ? new Date(resume.created_at).toLocaleDateString() : '—'}
                  </div>
                  <button className="btn btn-ghost btn-sm" onClick={() => navigate('/analyze')}>
                    Analyze
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {resumes.length > 0 && filtered.length === 0 && (
        <EmptyState
          icon={Search}
          title="No results found"
          message={`No CVs match "${searchQuery}". Try a different search term.`}
        />
      )}

      <ConfirmDialog
        open={!!deleteId}
        title="Delete CV"
        message="Are you sure you want to delete this CV? This action cannot be undone."
        onConfirm={() => { setDeleteId(null); }}
        onCancel={() => setDeleteId(null)}
      />
    </div>
  );
}
