import { useParams, useNavigate } from 'react-router-dom';
import { FileText, ArrowLeft, Search } from 'lucide-react';

export default function ResumeDetailPage() {
  const { resumeId } = useParams();
  const navigate = useNavigate();

  // Placeholder — in a real app, this would fetch resume data by ID
  return (
    <div>
      <div className="page-header">
        <button className="btn btn-ghost btn-sm mb-4" onClick={() => navigate('/resumes')}>
          <ArrowLeft size={16} />
          Back to CVs
        </button>
        <h1 className="page-header__title">CV Details</h1>
        <p className="page-header__subtitle">Resume #{resumeId}</p>
      </div>

      <div className="card">
        <div className="card-header flex items-center gap-2">
          <FileText size={18} />
          Resume Information
        </div>
        <div className="card-body">
          <p className="text-secondary">
            Detailed view for resume #{resumeId}. This page displays file metadata, candidate profile, extracted CV data, skills, and previous analysis results.
          </p>
          <div className="mt-6">
            <button className="btn btn-primary" onClick={() => navigate('/analyze')}>
              <Search size={18} />
              Analyze This CV
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
