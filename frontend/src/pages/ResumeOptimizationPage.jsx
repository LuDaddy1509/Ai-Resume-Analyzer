import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Sparkles,
  Download,
  FileText,
  TrendingUp,
  ChevronDown,
  ChevronRight,
  Search,
  Upload,
  AlertCircle,
  CheckCircle2,
} from 'lucide-react';
import { resumeAPI, jobDescriptionAPI, optimizationAPI } from '../services/api';
import PageLoader from '../components/PageLoader';
import EmptyState from '../components/EmptyState';
import ScoreBadge from '../components/ScoreBadge';

function Improvement({ value }) {
  if (value == null) return null;
  const positive = value > 0;
  return (
    <span
      className="badge"
      style={{
        background: positive ? 'var(--color-success-light)' : 'var(--color-error-light)',
        color: positive ? 'var(--color-success-text)' : 'var(--color-error-text)',
      }}
    >
      <TrendingUp size={13} />
      {positive ? '+' : ''}
      {Number(value).toFixed(1)}
    </span>
  );
}

function SkillsChips({ skills }) {
  if (!skills || skills.length === 0) return <span className="text-muted text-sm">—</span>;
  return (
    <div className="flex gap-2 flex-wrap">
      {skills.map((s, i) => (
        <span key={`${s}-${i}`} className="tag tag-primary">
          {s}
        </span>
      ))}
    </div>
  );
}

function ExperiencesList({ items }) {
  if (!items || items.length === 0) return <span className="text-muted text-sm">—</span>;
  return (
    <div style={{ display: 'grid', gap: 'var(--space-3)' }}>
      {items.map((exp, i) => {
        const bullets = exp.bullets || exp.achievements || [];
        const bulletsArr = typeof bullets === 'string' ? [bullets] : bullets;
        return (
          <div key={i}>
            <div className="font-semibold">
              {exp.position || 'Position'} {exp.company ? `· ${exp.company}` : ''}
            </div>
            {exp.description && (
              <div className="text-sm text-muted mt-1">{exp.description}</div>
            )}
            {bulletsArr.length > 0 && (
              <ul style={{ margin: 'var(--space-2) 0 0', paddingLeft: 'var(--space-5)' }}>
                {bulletsArr.map((b, j) => (
                  <li key={j} className="text-sm mt-1">
                    {b}
                  </li>
                ))}
              </ul>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default function ResumeOptimizationPage() {
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);
  const [jobDescriptions, setJobDescriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [optimizing, setOptimizing] = useState(false);
  const [error, setError] = useState(null);

  const [selectedId, setSelectedId] = useState(null);
  const [selectedJdId, setSelectedJdId] = useState('');
  const [result, setResult] = useState(null);
  const [previous, setPrevious] = useState([]);
  const [showPrevious, setShowPrevious] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [histData, jdData] = await Promise.all([
        resumeAPI.getHistory().catch(() => []),
        jobDescriptionAPI.getAll().catch(() => []),
      ]);
      setHistory(histData);
      setJobDescriptions(jdData);
      const first = histData.find((h) => h.analysis_id && h.resume_id) || histData[0];
      if (first) {
        setSelectedId(first.id);
        setSelectedJdId(first.job_description_id != null ? String(first.job_description_id) : '');
      }
    } catch {
      setError('Không thể tải dữ liệu. Kiểm tra kết nối server.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const selected = history.find((h) => h.id === selectedId) || null;

  const loadPrevious = useCallback(async (resumeId) => {
    if (!resumeId) {
      setPrevious([]);
      return;
    }
    try {
      const data = await optimizationAPI.getByResume(resumeId);
      setPrevious(data || []);
    } catch {
      setPrevious([]);
    }
  }, []);

  useEffect(() => {
    setResult(null);
    if (selected?.resume_id) {
      loadPrevious(selected.resume_id);
    } else {
      setPrevious([]);
    }
  }, [selectedId, selected?.resume_id, loadPrevious]);

  const handleOptimize = async () => {
    if (!selected?.resume_id) return;
    setOptimizing(true);
    setError(null);
    try {
      const data = await optimizationAPI.optimize(selected.resume_id, {
        analysis_id: selected.analysis_id || undefined,
        job_description_id: selectedJdId ? Number(selectedJdId) : undefined,
      });
      setResult(data);
      loadPrevious(selected.resume_id);
    } catch (err) {
      setError(err.response?.data?.detail || 'Optimization failed. Please try again.');
    } finally {
      setOptimizing(false);
    }
  };

  const handleExportPDF = async () => {
    if (!result) return;
    try {
      const resp = await optimizationAPI.exportPDF(result.id);
      const url = URL.createObjectURL(new Blob([resp.data], { type: 'application/pdf' }));
      const a = document.createElement('a');
      a.href = url;
      a.download = `optimized-resume-${result.id}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      setError('Không thể xuất PDF.');
    }
  };

  if (loading) return <PageLoader />;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-header__title">Resume Optimization</h1>
        <p className="page-header__subtitle">
          Rewrite your CV to match the job description and pass ATS screening.
        </p>
      </div>

      {error && (
        <div className="alert alert-warning mb-6" role="alert">
          <AlertCircle size={20} />
          <div style={{ flex: 1 }}>{error}</div>
          <button className="btn btn-sm btn-secondary" onClick={() => setError(null)}>
            Dismiss
          </button>
        </div>
      )}

      {history.length === 0 ? (
        <EmptyState
          icon={Sparkles}
          title="No CV to optimize"
          message="Import a CV first, then come back here to optimize it."
          action={
            <button className="btn btn-primary" onClick={() => navigate('/resumes/import')}>
              <Upload size={18} />
              Import CV
            </button>
          }
        />
      ) : (
        <>
          {/* Controls */}
          <div className="card" style={{ padding: 'var(--space-5)' }}>
            <div className="flex gap-4 flex-wrap items-end">
              <div style={{ flex: '1 1 260px' }}>
                <label className="form-label">Select CV</label>
                <select
                  className="form-select"
                  style={{ width: '100%' }}
                  value={selectedId || ''}
                  onChange={(e) => setSelectedId(Number(e.target.value))}
                >
                  {history.map((h) => (
                    <option key={h.id} value={h.id}>
                      {h.full_name || 'Unknown'} — {h.filename}
                    </option>
                  ))}
                </select>
              </div>
              <div style={{ flex: '1 1 260px' }}>
                <label className="form-label">Job Description (optional)</label>
                <select
                  className="form-select"
                  style={{ width: '100%' }}
                  value={selectedJdId}
                  onChange={(e) => setSelectedJdId(e.target.value)}
                >
                  <option value="">Use analysis-linked JD</option>
                  {jobDescriptions.map((jd) => (
                    <option key={jd.id} value={jd.id}>
                      {jd.title}
                    </option>
                  ))}
                </select>
              </div>
              <button
                className="btn btn-primary"
                onClick={handleOptimize}
                disabled={optimizing || !selected?.resume_id}
              >
                {optimizing ? (
                  <>
                    <span className="spinner-border spinner-border-sm" aria-hidden="true" />
                    Optimizing…
                  </>
                ) : (
                  <>
                    <Sparkles size={18} />
                    Optimize Resume
                  </>
                )}
              </button>
            </div>

            {selected && !selected.analysis_id && (
              <div className="alert alert-warning mt-4" role="alert">
                <AlertCircle size={18} />
                CV này chưa có phân tích kèm Job Description — tối ưu sẽ dùng nội dung CV thuần.
              </div>
            )}
          </div>

          {/* Result */}
          {result && result.status === 'completed' && (
            <div style={{ display: 'grid', gap: 'var(--space-6)', marginTop: 'var(--space-6)' }}>
              {/* Scores */}
              <div className="grid-3">
                <div className="card">
                  <div className="card-header">ATS Score</div>
                  <div className="flex items-end justify-between gap-3 mt-3 flex-wrap">
                    <div>
                      <div className="stat-card__label">Before</div>
                      <ScoreBadge score={Math.round(result.original_ats_score || 0)} />
                    </div>
                    <div>
                      <div className="stat-card__label">After</div>
                      <ScoreBadge score={Math.round(result.optimized_ats_score || 0)} />
                    </div>
                    <div>
                      <div className="stat-card__label">Change</div>
                      <Improvement value={result.ats_improvement} />
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="card-header">Match Score</div>
                  <div className="flex items-end justify-between gap-3 mt-3 flex-wrap">
                    <div>
                      <div className="stat-card__label">Before</div>
                      <ScoreBadge score={Math.round(result.original_match_score || 0)} />
                    </div>
                    <div>
                      <div className="stat-card__label">After</div>
                      <ScoreBadge score={Math.round(result.optimized_match_score || 0)} />
                    </div>
                    <div>
                      <div className="stat-card__label">Change</div>
                      <Improvement value={result.match_improvement} />
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="card-header">Status</div>
                  <div className="flex items-center gap-2 mt-3">
                    <CheckCircle2 size={18} color="var(--color-success)" />
                    <span className="font-semibold">Completed</span>
                  </div>
                  <div className="text-sm text-muted mt-1">
                    {result.optimization_notes?.length || 0} changes applied
                  </div>
                  <button className="btn btn-secondary btn-sm mt-3" onClick={handleExportPDF}>
                    <Download size={15} />
                    Export PDF
                  </button>
                </div>
              </div>

              {/* Summary */}
              <div className="card">
                <div className="card-header">Professional Summary</div>
                <div className="grid-2 mt-3" style={{ gap: 'var(--space-4)' }}>
                  <div>
                    <div className="stat-card__label mb-2">Original</div>
                    <div className="text-sm text-muted">{result.original_summary || '—'}</div>
                  </div>
                  <div>
                    <div className="stat-card__label mb-2">Optimized</div>
                    <div className="text-sm">{result.optimized_summary || '—'}</div>
                  </div>
                </div>
              </div>

              {/* Skills */}
              <div className="card">
                <div className="card-header">Skills</div>
                <div className="grid-2 mt-3" style={{ gap: 'var(--space-4)' }}>
                  <div>
                    <div className="stat-card__label mb-2">Original</div>
                    <SkillsChips skills={result.original_skills} />
                  </div>
                  <div>
                    <div className="stat-card__label mb-2">Optimized</div>
                    <SkillsChips skills={result.optimized_skills} />
                  </div>
                </div>
              </div>

              {/* Experiences */}
              <div className="card">
                <div className="card-header">Work Experience</div>
                <div className="grid-2 mt-3" style={{ gap: 'var(--space-4)' }}>
                  <div>
                    <div className="stat-card__label mb-2">Original</div>
                    <ExperiencesList items={result.original_experiences} />
                  </div>
                  <div>
                    <div className="stat-card__label mb-2">Optimized</div>
                    <ExperiencesList items={result.optimized_experiences} />
                  </div>
                </div>
              </div>

              {/* Notes */}
              {result.optimization_notes?.length > 0 && (
                <div className="card">
                  <div className="card-header">Optimization Notes</div>
                  <ul style={{ margin: 'var(--space-3) 0 0', paddingLeft: 'var(--space-5)' }}>
                    {result.optimization_notes.map((note, i) => (
                      <li key={i} className="text-sm mt-2">
                        {note}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {result && result.status === 'failed' && (
            <div className="alert alert-error mt-6" role="alert">
              <AlertCircle size={20} />
              Optimization failed. {(result.optimization_notes || []).join(' ')}
            </div>
          )}

          {/* Previous optimizations */}
          {selected?.resume_id && previous.length > 0 && (
            <div className="card mt-6">
              <button
                className="card-header flex items-center justify-between"
                style={{ width: '100%', border: 'none', background: 'none', cursor: 'pointer', textAlign: 'left' }}
                onClick={() => setShowPrevious((v) => !v)}
              >
                <span className="flex items-center gap-2">
                  {showPrevious ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
                  Previous Optimizations ({previous.length})
                </span>
              </button>
              {showPrevious && (
                <div className="mt-3" style={{ overflowX: 'auto' }}>
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Date</th>
                        <th>ATS Before</th>
                        <th>ATS After</th>
                        <th>Status</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>
                      {previous.map((opt) => (
                        <tr key={opt.id}>
                          <td>#{opt.id}</td>
                          <td className="text-sm text-muted">
                            {opt.created_at ? new Date(opt.created_at).toLocaleString() : '—'}
                          </td>
                          <td>{Math.round(opt.original_ats_score || 0)}</td>
                          <td>{Math.round(opt.optimized_ats_score || 0)}</td>
                          <td>
                            <span className={`badge ${opt.status === 'completed' ? 'badge-success' : 'badge-warning'}`}>
                              {opt.status}
                            </span>
                          </td>
                          <td>
                            <button className="btn btn-ghost btn-sm" onClick={() => setResult(opt)}>
                              <FileText size={14} />
                              View
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {selected?.resume_id && previous.length === 0 && !result && (
            <div className="empty-state" style={{ marginTop: 'var(--space-6)' }}>
              <div className="empty-state__icon">
                <Search size={56} strokeWidth={1.5} />
              </div>
              <h3 className="empty-state__title">No optimization yet</h3>
              <p className="empty-state__message">
                Select a CV and click "Optimize Resume" to get an ATS-tailored version.
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
}