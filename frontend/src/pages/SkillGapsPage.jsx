import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Target,
  BookOpen,
  ListChecks,
  Lightbulb,
  ChevronDown,
  ChevronRight,
  Upload,
  AlertCircle,
  CheckCircle2,
  RefreshCw,
  ExternalLink,
} from 'lucide-react';
import { resumeAPI, skillGapAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import PageLoader from '../components/PageLoader';
import EmptyState from '../components/EmptyState';

function PriorityBadge({ priority }) {
  const cls =
    priority === 'high' ? 'badge-error' : priority === 'medium' ? 'badge-warning' : 'badge-info';
  return <span className={`badge ${cls}`}>{priority}</span>;
}

function MetricBar({ label, value, suffix = '%' }) {
  const pct = Math.min(100, Math.round((value ?? 0) * 100));
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-muted">{label}</span>
        <span className="font-medium">
          {value == null ? '—' : `${Number(value).toFixed(0)}${suffix}`}
        </span>
      </div>
      <div className="progress-bar">
        <div className="progress-bar__fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function LearningPath({ path }) {
  const [open, setOpen] = useState(false);
  if (!path) return null;
  return (
    <div className="mt-3">
      <button
        className="btn btn-ghost btn-sm"
        onClick={() => setOpen((v) => !v)}
      >
        {open ? <ChevronDown size={15} /> : <ChevronRight size={15} />}
        Learning Path ({path.estimated_weeks || '?'} weeks)
      </button>
      {open && (
        <div className="mt-3" style={{ display: 'grid', gap: 'var(--space-4)' }}>
          {path.milestones?.length > 0 && (
            <div>
              <div className="font-semibold flex items-center gap-2 mb-2">
                <ListChecks size={16} /> Milestones
              </div>
              <ol style={{ margin: 0, paddingLeft: 'var(--space-5)' }}>
                {path.milestones.map((m, i) => (
                  <li key={i} className="text-sm mt-2">
                    <span className="badge badge-neutral mr-2">Week {m.week}</span>
                    <span className="font-medium">{m.phase}</span> — {m.goal}
                    {m.deliverable && <div className="text-muted">Deliverable: {m.deliverable}</div>}
                  </li>
                ))}
              </ol>
            </div>
          )}
          {path.resources?.length > 0 && (
            <div>
              <div className="font-semibold flex items-center gap-2 mb-2">
                <BookOpen size={16} /> Resources
              </div>
              <div style={{ display: 'grid', gap: 'var(--space-2)' }}>
                {path.resources.map((r, i) => (
                  <div key={i} className="flex items-start justify-between gap-3 text-sm">
                    <div style={{ minWidth: 0 }}>
                      <span className={`badge ${r.type === 'free' ? 'badge-success' : r.type === 'paid' ? 'badge-warning' : 'badge-neutral'} mr-2`}>
                        {r.type}
                      </span>
                      <span className="font-medium">{r.title}</span>
                      {r.description && (
                        <div className="text-muted" style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {r.description}
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-muted" style={{ flexShrink: 0 }}>
                      {r.cost && <span>{r.cost}</span>}
                      {r.url && (
                        <a href={r.url} target="_blank" rel="noreferrer" className="btn btn-ghost btn-sm">
                          <ExternalLink size={13} />
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          {path.project_ideas?.length > 0 && (
            <div>
              <div className="font-semibold flex items-center gap-2 mb-2">
                <Lightbulb size={16} /> Project Ideas
              </div>
              <ul style={{ margin: 0, paddingLeft: 'var(--space-5)' }}>
                {path.project_ideas.map((p, i) => (
                  <li key={i} className="text-sm mt-1">
                    {p}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function SkillGapsPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [gaps, setGaps] = useState([]);
  const [progress, setProgress] = useState([]);
  const [analyzed, setAnalyzed] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const histData = await resumeAPI.getHistory().catch(() => []);
      setHistory(histData);
      const first = histData.find((h) => h.analysis_id && h.resume_id) || histData[0];
      if (first) setSelectedId(first.id);
    } catch {
      setError('Không thể tải dữ liệu. Kiểm tra kết nối server.');
    } finally {
      setLoading(false);
    }
  }, []);

  const loadProgress = useCallback(async () => {
    if (!user?.id) return;
    try {
      setProgress(await skillGapAPI.getProgress(user.id));
    } catch {
      setProgress([]);
    }
  }, [user?.id]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    loadProgress();
  }, [loadProgress]);

  const selected = history.find((h) => h.id === selectedId) || null;

  const handleAnalyze = async () => {
    if (!selected?.analysis_id || !selected?.resume_id) return;
    setAnalyzing(true);
    setError(null);
    try {
      const data = await skillGapAPI.analyze(selected.analysis_id, selected.resume_id);
      setGaps(data || []);
      setAnalyzed(true);
      loadProgress();
    } catch (err) {
      setError(err.response?.data?.detail || 'Skill gap analysis failed.');
      setGaps([]);
      setAnalyzed(true);
    } finally {
      setAnalyzing(false);
    }
  };

  const getProgressFor = (skillName) =>
    progress.find((p) => p.skill_name.toLowerCase() === skillName.toLowerCase()) || null;

  const handleProgress = async (skillName, status) => {
    if (!user?.id) return;
    try {
      const existing = getProgressFor(skillName);
      if (existing) {
        await skillGapAPI.updateProgress(existing.id, {
          skill_name: existing.skill_name,
          status,
          proficiency_level: status === 'proficient' ? 'intermediate' : existing.proficiency_level,
        });
      } else {
        await skillGapAPI.createProgress(user.id, { skill_name: skillName, status });
      }
      loadProgress();
    } catch {
      setError('Không thể cập nhật tiến độ.');
    }
  };

  if (loading) return <PageLoader />;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-header__title">Skill Gap Analysis</h1>
        <p className="page-header__subtitle">
          Find missing skills vs the job description and follow a personalized learning path.
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
          icon={Target}
          title="No CV to analyze"
          message="Import and analyze a CV first to find your skill gaps."
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
              <div style={{ flex: '1 1 300px' }}>
                <label className="form-label">Select CV analysis</label>
                <select
                  className="form-select"
                  style={{ width: '100%' }}
                  value={selectedId || ''}
                  onChange={(e) => {
                    setSelectedId(Number(e.target.value));
                    setGaps([]);
                    setAnalyzed(false);
                  }}
                >
                  {history.map((h) => (
                    <option key={h.id} value={h.id}>
                      {h.full_name || 'Unknown'} — {h.filename}
                      {h.match_score != null ? ` (${h.match_score}%)` : ''}
                    </option>
                  ))}
                </select>
              </div>
              <button
                className="btn btn-primary"
                onClick={handleAnalyze}
                disabled={analyzing || !selected?.analysis_id || !selected?.resume_id}
              >
                {analyzing ? (
                  <>
                    <span className="spinner-border spinner-border-sm" aria-hidden="true" />
                    Analyzing…
                  </>
                ) : (
                  <>
                    <Target size={18} />
                    Analyze Skill Gaps
                  </>
                )}
              </button>
            </div>

            {selected && !selected.analysis_id && (
              <div className="alert alert-warning mt-4" role="alert">
                <AlertCircle size={18} />
                CV này không có phân tích kèm Job Description (thiếu dữ liệu kỹ năng yêu cầu).
                Hãy phân tích lại CV có kèm JD để xem skill gaps.
              </div>
            )}
          </div>

          {!user?.id && (
            <div className="alert alert-info mt-4" role="alert">
              <AlertCircle size={18} />
              Đăng nhập để theo dõi tiến độ học tập của bạn.
            </div>
          )}

          {/* Results */}
          {analyzed && !analyzing && gaps.length === 0 && (
            <EmptyState
              icon={CheckCircle2}
              title="No skill gaps detected"
              message={
                selected?.analysis_id
                  ? 'CV của bạn đã khớp tất cả kỹ năng yêu cầu của Job Description này. Tuyệt vời!'
                  : 'Chọn một CV có phân tích kèm Job Description để xem kết quả.'
              }
            />
          )}

          {gaps.length > 0 && (
            <div style={{ display: 'grid', gap: 'var(--space-4)', marginTop: 'var(--space-6)' }}>
              {gaps.map((gap) => {
                const pg = getProgressFor(gap.skill_name);
                return (
                  <div key={gap.id} className="card" style={{ padding: 'var(--space-5)' }}>
                    <div className="flex items-center justify-between flex-wrap gap-3">
                      <div className="flex items-center gap-3">
                        <div
                          style={{
                            width: 40,
                            height: 40,
                            borderRadius: 'var(--radius-md)',
                            background: 'var(--color-primary-50)',
                            color: 'var(--color-primary)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            flexShrink: 0,
                          }}
                        >
                          <Target size={20} />
                        </div>
                        <div>
                          <div className="font-semibold">{gap.skill_name}</div>
                          <div className="text-sm text-muted">
                            {gap.current_proficiency || 'none'} → {gap.target_proficiency || 'proficient'}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <PriorityBadge priority={gap.priority} />
                        {pg && (
                          <span className={`badge ${pg.status === 'proficient' ? 'badge-success' : 'badge-info'}`}>
                            {pg.status === 'proficient' ? 'Proficient' : 'Learning'}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="grid-3 mt-4" style={{ gap: 'var(--space-4)' }}>
                      <MetricBar label="Market demand" value={gap.market_demand_score} />
                      <MetricBar label="Learnability" value={gap.learnability_score} />
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-muted">Impact on match</span>
                          <span className="font-medium">
                            {gap.impact_on_match_score == null ? '—' : `+${Number(gap.impact_on_match_score).toFixed(1)} pts`}
                          </span>
                        </div>
                        <div className="progress-bar">
                          <div
                            className="progress-bar__fill progress-bar__fill--success"
                            style={{ width: `${Math.min(100, gap.impact_on_match_score || 0)}%` }}
                          />
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between flex-wrap gap-3 mt-4">
                      <LearningPath path={gap.learning_path} />
                      <div className="flex items-center gap-2">
                        {!pg && (
                          <button className="btn btn-secondary btn-sm" onClick={() => handleProgress(gap.skill_name, 'learning')}>
                            <BookOpen size={15} />
                            Start learning
                          </button>
                        )}
                        {pg && pg.status !== 'proficient' && (
                          <button className="btn btn-success btn-sm" onClick={() => handleProgress(gap.skill_name, 'proficient')}>
                            <CheckCircle2 size={15} />
                            Mark proficient
                          </button>
                        )}
                        {pg && pg.status === 'proficient' && (
                          <button className="btn btn-ghost btn-sm" onClick={() => handleProgress(gap.skill_name, 'learning')}>
                            <RefreshCw size={15} />
                            Reset
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
}