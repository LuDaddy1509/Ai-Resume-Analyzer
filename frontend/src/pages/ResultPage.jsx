import { useLocation, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import {
  ArrowLeft,
  Download,
  RefreshCw,
  Home,
  History,
  Zap,
  CheckCircle,
  User,
  Mail,
  Briefcase,
} from 'lucide-react';
import ScoreCard from '../components/ScoreCard';
import SkillsRadar from '../components/SkillsRadar';
import SuggestionList from '../components/SuggestionList';
import { resumeAPI } from '../services/api';

export default function ResultPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const resumeData = location.state?.resumeData;
  const [exporting, setExporting] = useState(false);

  const handleExport = async (type) => {
    const historyId = resumeData?.history_id;
    if (!historyId) return;

    setExporting(true);
    try {
      const response = type === 'pdf'
        ? await resumeAPI.exportPDF(historyId)
        : await resumeAPI.exportExcel(historyId);

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = `resume-analysis-${resumeData.full_name || 'report'}.${type === 'pdf' ? 'pdf' : 'xlsx'}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch {
      alert('Export failed. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  if (!resumeData) {
    return (
      <div className="empty-state">
        <div className="empty-state__icon">
          <Zap size={56} strokeWidth={1.5} />
        </div>
        <h3 className="empty-state__title">No analysis data</h3>
        <p className="empty-state__message">
          Please analyze a CV first to view results.
        </p>
        <button className="btn btn-primary" onClick={() => navigate('/analyze')}>
          <ArrowLeft size={18} />
          Go to Analyze
        </button>
      </div>
    );
  }

  const analysis = resumeData.analysis;

  return (
    <div style={{ maxWidth: 900, margin: '0 auto' }}>
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-4 mb-8">
        <div>
          <button className="btn btn-ghost btn-sm mb-3" onClick={() => navigate('/analyze')}>
            <ArrowLeft size={16} />
            Back to Analyze
          </button>
          <h1 className="page-header__title">Analysis Result</h1>
          <div className="flex items-center gap-4 mt-2 text-sm text-secondary">
            <span className="flex items-center gap-1">
              <User size={14} /> {resumeData.full_name || 'Unknown'}
            </span>
            {resumeData.email && (
              <span className="flex items-center gap-1">
                <Mail size={14} /> {resumeData.email}
              </span>
            )}
          </div>
        </div>
        <div className="flex gap-2 flex-wrap">
          <button className="btn btn-secondary btn-sm" onClick={() => handleExport('pdf')} disabled={exporting || !resumeData.history_id}>
            <Download size={16} />
            PDF
          </button>
          <button className="btn btn-secondary btn-sm" onClick={() => handleExport('excel')} disabled={exporting || !resumeData.history_id}>
            <Download size={16} />
            Excel
          </button>
          <button className="btn btn-ghost btn-sm" onClick={() => navigate('/analyze')}>
            <RefreshCw size={16} />
            Analyze Another
          </button>
        </div>
      </div>

      {/* Score Cards */}
      {analysis && (
        <div className="grid-2 mb-6">
          <ScoreCard
            score={analysis.match_score}
            title="Match Score"
            subtitle="CV-Job compatibility"
          />
          {analysis.ats_score != null && (
            <ScoreCard
              score={analysis.ats_score}
              title="ATS Score"
              subtitle="Applicant Tracking System"
            />
          )}
        </div>
      )}

      {/* Strengths */}
      {analysis?.strengths?.length > 0 && (
        <div className="panel mb-5">
          <div className="panel__header panel__header--success">
            <CheckCircle size={18} />
            <span>Strengths</span>
          </div>
          <div className="panel__body">
            <ul className="panel__list">
              {analysis.strengths.map((item, i) => (
                <li key={i}>
                  <span className="panel__list-icon">
                    <CheckCircle size={16} color="var(--color-success)" />
                  </span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Suggestions */}
      {analysis && <SuggestionList suggestions={analysis.suggestions} />}

      {/* Skill Analysis */}
      {analysis && (
        <SkillsRadar
          matchedSkills={analysis.matched_skills}
          missingSkills={analysis.missing_skills}
        />
      )}

      {/* Personal Info */}
      <div className="card mb-5">
        <div className="card-header flex items-center gap-2">
          <User size={18} />
          Candidate Information
        </div>
        <div className="card-body">
          <div className="grid-3">
            <div>
              <div className="text-sm text-muted mb-1">Full Name</div>
              <div className="font-medium">{resumeData.full_name || 'Not provided'}</div>
            </div>
            <div>
              <div className="text-sm text-muted mb-1">Email</div>
              <div className="font-medium">{resumeData.email || 'Not provided'}</div>
            </div>
            <div>
              <div className="text-sm text-muted mb-1">Phone</div>
              <div className="font-medium">{resumeData.phone || 'Not provided'}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Skills */}
      {resumeData.skills?.length > 0 && (
        <div className="card mb-5">
          <div className="card-header flex items-center gap-2">
            <Zap size={18} />
            Extracted Skills ({resumeData.skills.length})
          </div>
          <div className="card-body">
            <div className="flex flex-wrap gap-2">
              {resumeData.skills.map((skill) => (
                <span key={skill} className="tag tag-primary">{skill}</span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Experience */}
      {resumeData.experiences?.length > 0 && (
        <div className="card mb-5">
          <div className="card-header flex items-center gap-2">
            <Briefcase size={18} />
            Work Experience
          </div>
          <div className="card-body">
            {resumeData.experiences.map((exp, idx) => (
              <div key={idx} style={{
                paddingBottom: 'var(--space-4)',
                marginBottom: idx < resumeData.experiences.length - 1 ? 'var(--space-4)' : 0,
                borderBottom: idx < resumeData.experiences.length - 1 ? '1px solid var(--color-border-subtle)' : 'none',
              }}>
                <div className="font-semibold">{exp.position}</div>
                <div className="text-sm text-secondary">{exp.company} — {exp.dates}</div>
                {exp.bullets?.length > 0 && (
                  <ul style={{ paddingLeft: 'var(--space-5)', marginTop: 'var(--space-2)' }}>
                    {exp.bullets.map((b, i) => (
                      <li key={i} className="text-sm" style={{ marginBottom: 'var(--space-1)', listStyleType: 'disc' }}>{b}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Disclaimer */}
      <div className="alert alert-info" style={{ fontSize: 'var(--text-sm)' }}>
        <Zap size={16} />
        <span>This AI-generated evaluation is advisory and may require human review. Results have been saved automatically.</span>
      </div>

      {/* Bottom Actions */}
      <div className="flex justify-center gap-3 mt-8 mb-4">
        <button className="btn btn-primary" onClick={() => navigate('/dashboard')}>
          <Home size={18} />
          Dashboard
        </button>
        <button className="btn btn-secondary" onClick={() => navigate('/analysis-history')}>
          <History size={18} />
          View History
        </button>
      </div>
    </div>
  );
}
