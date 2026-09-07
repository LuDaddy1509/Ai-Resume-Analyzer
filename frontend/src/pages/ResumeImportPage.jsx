import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, Search, ArrowRight } from 'lucide-react';
import FileDropZone from '../components/FileDropZone';
import ProcessingStepper from '../components/ProcessingStepper';
import { resumeAPI } from '../services/api';
import { useToast } from '../contexts/ToastContext';

const UPLOAD_STEPS = [
  'Uploading document',
  'Validating file type and size',
  'Checking if document is a CV/resume',
  'Extracting text',
  'Extracting structured information',
  'Preparing extracted data for review',
  'Saving CV/resume',
];

export default function ResumeImportPage() {
  const navigate = useNavigate();
  const toast = useToast();

  const [file, setFile] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const [stepError, setStepError] = useState(false);
  const [extractedData, setExtractedData] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  const handleFileSelect = (selectedFile) => {
    const ext = selectedFile.name.split('.').pop().toLowerCase();
    if (!['pdf', 'docx'].includes(ext)) {
      setErrorMessage('Only PDF and DOCX files are accepted.');
      return;
    }
    if (selectedFile.size > 10 * 1024 * 1024) {
      setErrorMessage('File size must be under 10MB.');
      return;
    }
    setFile(selectedFile);
    setErrorMessage('');
    setExtractedData(null);
    setCurrentStep(-1);
    setStepError(false);
  };

  const handleUpload = async () => {
    if (!file) return;
    setProcessing(true);
    setStepError(false);
    setErrorMessage('');
    setExtractedData(null);

    // Simulate stepping through stages
    for (let i = 0; i < UPLOAD_STEPS.length - 1; i++) {
      setCurrentStep(i);
      await new Promise((r) => setTimeout(r, 400 + Math.random() * 300));
    }

    try {
      const data = await resumeAPI.parseResume(file);
      setCurrentStep(UPLOAD_STEPS.length);

      // Check if it's a valid CV
      if (data.validation && !data.validation.is_resume) {
        setStepError(true);
        setCurrentStep(2);
        setErrorMessage('This document does not appear to be a CV or resume. Please upload a valid CV in PDF or DOCX format.');
        setProcessing(false);
        return;
      }

      setExtractedData(data);
      toast.success('CV Imported', 'Document successfully processed and ready for review.');
    } catch (err) {
      setStepError(true);
      const msg = err.response?.data?.message || 'Failed to process the document. Please try again.';
      setErrorMessage(msg);
    } finally {
      setProcessing(false);
    }
  };

  const handleSaveAndAnalyze = () => {
    if (extractedData) {
      navigate('/result', { state: { resumeData: extractedData.data || extractedData } });
    }
  };

  const handleClear = () => {
    setFile(null);
    setExtractedData(null);
    setCurrentStep(-1);
    setStepError(false);
    setErrorMessage('');
  };

  const resumeInfo = extractedData?.data || extractedData;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-header__title">Import CV / Resume</h1>
        <p className="page-header__subtitle">Upload your document to extract and save your CV information.</p>
      </div>

      {/* Drop Zone */}
      <div className="card mb-6">
        <div className="card-body">
          <FileDropZone
            onFileSelect={handleFileSelect}
            accept=".pdf,.docx"
            maxSizeMB={10}
            file={file}
            onClear={handleClear}
          />
        </div>
      </div>

      {/* Error */}
      {errorMessage && (
        <div className="alert alert-error mb-6" role="alert">
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Processing Stepper */}
      {(processing || currentStep >= 0) && !extractedData && (
        <div className="card mb-6">
          <div className="card-header flex items-center gap-2">
            <Upload size={18} />
            Processing Document
          </div>
          <div className="card-body">
            <ProcessingStepper steps={UPLOAD_STEPS} currentStep={currentStep} error={stepError} />
          </div>
        </div>
      )}

      {/* Extracted Data Review */}
      {resumeInfo && (
        <div className="card mb-6">
          <div className="card-header flex items-center gap-2">
            <FileText size={18} />
            Extracted CV Information
          </div>
          <div className="card-body">
            {/* Candidate info */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-3">Candidate Information</h3>
              <div className="grid-2">
                <div>
                  <div className="text-sm text-muted">Full Name</div>
                  <div className="font-medium">{resumeInfo.full_name || 'Not provided'}</div>
                </div>
                <div>
                  <div className="text-sm text-muted">Email</div>
                  <div className="font-medium">{resumeInfo.email || 'Not provided'}</div>
                </div>
                <div>
                  <div className="text-sm text-muted">Phone</div>
                  <div className="font-medium">{resumeInfo.phone || 'Not provided'}</div>
                </div>
              </div>
            </div>

            <hr className="divider" />

            {/* Skills */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-3">Skills</h3>
              {resumeInfo.skills?.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {resumeInfo.skills.map((skill) => (
                    <span key={skill} className="tag tag-primary">{skill}</span>
                  ))}
                </div>
              ) : (
                <p className="text-muted">Not provided</p>
              )}
            </div>

            <hr className="divider" />

            {/* Experience */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-3">Work Experience</h3>
              {resumeInfo.experiences?.length > 0 ? (
                <div style={{ display: 'grid', gap: 'var(--space-4)' }}>
                  {resumeInfo.experiences.map((exp, idx) => (
                    <div key={idx} style={{ paddingBottom: 'var(--space-4)', borderBottom: idx < resumeInfo.experiences.length - 1 ? '1px solid var(--color-border-subtle)' : 'none' }}>
                      <div className="font-semibold">{exp.position || 'Not provided'}</div>
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
              ) : (
                <p className="text-muted">Not provided</p>
              )}
            </div>
          </div>

          {/* Save Actions */}
          <div className="card-footer flex justify-end gap-3">
            <button className="btn btn-secondary" onClick={handleClear}>
              Cancel
            </button>
            <button className="btn btn-accent" onClick={handleSaveAndAnalyze}>
              <Search size={18} />
              Save & Analyze
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      )}

      {/* Upload button */}
      {file && !processing && !extractedData && (
        <button className="btn btn-primary btn-lg" style={{ width: '100%' }} onClick={handleUpload}>
          <Upload size={20} />
          Upload & Process
        </button>
      )}
    </div>
  );
}
