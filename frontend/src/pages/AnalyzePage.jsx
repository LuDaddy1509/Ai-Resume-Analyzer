import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, FileText, Upload, Calendar, Zap } from 'lucide-react';
import { resumeAPI } from '../services/api';
import FileDropZone from '../components/FileDropZone';
import ProcessingStepper from '../components/ProcessingStepper';
import EmptyState from '../components/EmptyState';
import PageLoader from '../components/PageLoader';
import { useToast } from '../contexts/ToastContext';

const ANALYSIS_STEPS = [
  'Loading CV data',
  'Preparing extracted content',
  'Evaluating ATS compatibility',
  'Evaluating work experience',
  'Evaluating education',
  'Evaluating skills & content quality',
  'Generating strengths & weaknesses',
  'Generating suggestions & advice',
  'Saving analysis result',
];

export default function AnalyzePage() {
  const navigate = useNavigate();
  const toast = useToast();

  const [savedResumes, setSavedResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  // Direct upload mode
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');

  // Analysis state
  const [analyzing, setAnalyzing] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const [analysisError, setAnalysisError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    loadResumes();
  }, []);

  const loadResumes = async () => {
    try {
      const data = await resumeAPI.getHistory();
      setSavedResumes(data);
    } catch {
      // OK if fails, can still upload directly
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setAnalyzing(true);
    setAnalysisError(false);
    setErrorMessage('');

    // Step through analysis stages
    for (let i = 0; i < ANALYSIS_STEPS.length - 1; i++) {
      setCurrentStep(i);
      await new Promise((r) => setTimeout(r, 350 + Math.random() * 400));
    }

    try {
      const data = await resumeAPI.parseResume(file, jobDescription);
      setCurrentStep(ANALYSIS_STEPS.length);
      toast.success('Analysis Complete', 'Your CV has been analyzed successfully.');

      // Navigate to result
      setTimeout(() => {
        navigate('/result', { state: { resumeData: data.data || data } });
      }, 500);
    } catch (err) {
      setAnalysisError(true);
      const msg = err.response?.data?.message || 'Analysis failed. Please try again.';
      setErrorMessage(msg);
      setAnalyzing(false);
    }
  };

  const filteredResumes = savedResumes.filter((r) => {
    const q = searchQuery.toLowerCase();
    return !q || r.full_name?.toLowerCase().includes(q) || r.filename?.toLowerCase().includes(q);
  });

  if (loading) return <PageLoader />;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-header__title">Analyze CV</h1>
        <p className="page-header__subtitle">
          Upload a CV and optionally provide a job description for AI analysis.
        </p>
      </div>

      {/* Upload area */}
      <div className="card mb-6">
        <div className="card-header flex items-center gap-2">
          <Upload size={18} />
          Upload CV for Analysis
        </div>
        <div className="card-body">
          <FileDropZone
            onFileSelect={(f) => { setFile(f); setErrorMessage(''); }}
            accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
            maxSizeMB={10}
            file={file}
            onClear={() => { setFile(null); setErrorMessage(''); }}
          />

          {/* Job Description */}
          <div className="form-group mt-6">
            <label className="form-label" htmlFor="analyze-jd">
              Job Description (optional)
            </label>
            <textarea
              id="analyze-jd"
              className="form-textarea"
              rows={4}
              placeholder="Paste the job description here for skill matching and ATS scoring..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              disabled={analyzing}
            />
            <div className="form-hint">
              Adding a job description enables match scoring and skill gap analysis.
            </div>
          </div>
        </div>
      </div>

      {/* Error */}
      {errorMessage && (
        <div className="alert alert-error mb-6" role="alert">
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Processing Stepper */}
      {analyzing && (
        <div className="card mb-6">
          <div className="card-header flex items-center gap-2">
            <Zap size={18} />
            AI Analysis in Progress
          </div>
          <div className="card-body">
            <ProcessingStepper steps={ANALYSIS_STEPS} currentStep={currentStep} error={analysisError} />
          </div>
        </div>
      )}

      {/* Analyze button */}
      {file && !analyzing && (
        <button className="btn btn-primary btn-lg mb-8" style={{ width: '100%' }} onClick={handleAnalyze} disabled={analyzing}>
          <Search size={20} />
          Analyze CV
        </button>
      )}

      {/* Disclaimer */}
      <div className="alert alert-info mb-6" style={{ fontSize: 'var(--text-sm)' }}>
        <Zap size={16} />
        <span>AI-generated evaluation is advisory and may require human review. Results are saved automatically after successful analysis.</span>
      </div>

      {/* Previously analyzed CVs */}
      {savedResumes.length > 0 && (
        <div className="card">
          <div className="card-header flex items-center gap-2">
            <FileText size={18} />
            Previously Analyzed CVs
          </div>
          <div className="card-body">
            <div className="search-input-wrapper mb-4">
              <Search size={18} className="search-icon" />
              <input
                className="search-input"
                placeholder="Search saved CVs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            {filteredResumes.length > 0 ? (
              <div style={{ display: 'grid', gap: 'var(--space-3)' }}>
                {filteredResumes.slice(0, 10).map((r) => (
                  <div key={r.id} className="flex items-center justify-between" style={{
                    padding: 'var(--space-3) var(--space-4)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--color-border-subtle)',
                  }}>
                    <div className="flex items-center gap-3" style={{ minWidth: 0 }}>
                      <FileText size={18} color="var(--color-primary)" />
                      <div style={{ minWidth: 0 }}>
                        <div className="font-medium text-sm" style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {r.full_name || 'Unknown'}
                        </div>
                        <div className="text-xs text-muted">{r.filename}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-muted">
                      <Calendar size={12} />
                      {r.created_at ? new Date(r.created_at).toLocaleDateString() : '—'}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted text-center" style={{ padding: 'var(--space-6)' }}>No matching CVs found.</p>
            )}
          </div>
        </div>
      )}

      {savedResumes.length === 0 && !file && (
        <EmptyState
          icon={FileText}
          title="No saved CVs"
          message="Upload a CV above to start analysis, or import one first."
          action={
            <button className="btn btn-secondary" onClick={() => navigate('/resumes/import')}>
              <Upload size={18} />
              Import CV First
            </button>
          }
        />
      )}
    </div>
  );
}