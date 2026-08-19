import { useNavigate } from 'react-router-dom';
import {
  Upload,
  Search,
  BarChart3,
  Zap,
  Shield,
  Target,
  Lightbulb,
  ArrowRight,
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import Navbar from '../components/Navbar';

const features = [
  {
    icon: Upload,
    color: 'var(--color-primary)',
    bg: 'var(--color-primary-50)',
    title: 'Import & Save CVs',
    description: 'Upload your CV in PDF or DOCX format. Your documents are securely stored and ready for analysis.',
  },
  {
    icon: Search,
    color: 'var(--color-accent)',
    bg: 'var(--color-accent-light)',
    title: 'AI-Powered Analysis',
    description: 'Our AI independently evaluates your CV across multiple dimensions for a comprehensive assessment.',
  },
  {
    icon: BarChart3,
    color: 'var(--color-info)',
    bg: 'var(--color-info-light)',
    title: 'Detailed Score Breakdown',
    description: 'View overall, ATS, skills, experience, and education scores with clear visual indicators.',
  },
  {
    icon: Target,
    color: 'var(--color-success)',
    bg: 'var(--color-success-light)',
    title: 'Strengths & Weaknesses',
    description: 'Identify what makes your CV stand out and discover areas that need improvement.',
  },
  {
    icon: Lightbulb,
    color: 'var(--color-warning)',
    bg: 'var(--color-warning-light)',
    title: 'Actionable Suggestions',
    description: 'Receive practical advice and prioritized suggestions to strengthen your professional profile.',
  },
  {
    icon: Shield,
    color: 'var(--color-error)',
    bg: 'var(--color-error-light)',
    title: 'ATS Compatibility',
    description: 'Check how well your CV performs against Applicant Tracking Systems used by employers.',
  },
  {
    icon: Zap,
    color: 'var(--color-primary)',
    bg: 'var(--color-primary-50)',
    title: 'Save & Review History',
    description: 'Access your analysis results anytime. Track your progress and improvements over time.',
  },
];

export default function HomePage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  return (
    <>
      <Navbar />

      {/* Hero */}
      <section className="hero">
        <div className="hero__badge">
          <Zap size={14} />
          AI-Powered CV Analysis
        </div>
        <h1 className="hero__title">
          Build a Stronger CV with{' '}
          <span className="hero__title-gradient">AI</span>
        </h1>
        <p className="hero__description">
          Import your CV, receive an independent AI evaluation, and discover practical ways to improve your professional profile.
        </p>
        <div className="hero__actions">
          {isAuthenticated ? (
            <button className="btn btn-primary btn-lg" onClick={() => navigate('/dashboard')}>
              Go to Dashboard
              <ArrowRight size={20} />
            </button>
          ) : (
            <>
              <button className="btn btn-primary btn-lg" onClick={() => navigate('/register')}>
                Get Started
                <ArrowRight size={20} />
              </button>
              <button className="btn btn-secondary btn-lg" onClick={() => navigate('/login')}>
                Log In
              </button>
            </>
          )}
        </div>
      </section>

      {/* Features */}
      <section id="features" style={{ background: 'var(--color-bg-subtle)', paddingTop: 'var(--space-8)', paddingBottom: 'var(--space-16)' }}>
        <div style={{ textAlign: 'center', marginBottom: 'var(--space-8)', padding: '0 var(--space-6)' }}>
          <h2 style={{ fontSize: 'var(--text-3xl)', fontWeight: 'var(--weight-bold)', color: 'var(--color-text)' }}>
            Everything you need to optimize your CV
          </h2>
          <p style={{ color: 'var(--color-text-secondary)', marginTop: 'var(--space-3)', fontSize: 'var(--text-lg)', maxWidth: 600, margin: 'var(--space-3) auto 0' }}>
            A complete suite of tools to analyze, improve, and track your professional profile.
          </p>
        </div>
        <div className="features-grid">
          {features.map(({ icon: Icon, color, bg, title, description }) => (
            <div key={title} className="feature-card">
              <div className="feature-card__icon" style={{ background: bg, color }}>
                <Icon size={24} />
              </div>
              <h3 className="feature-card__title">{title}</h3>
              <p className="feature-card__description">{description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer style={{ textAlign: 'center', padding: 'var(--space-8) var(--space-6)', borderTop: '1px solid var(--color-border)', color: 'var(--color-text-muted)', fontSize: 'var(--text-sm)' }}>
        © {new Date().getFullYear()} AI Resume Analyzer. Built for career development.
      </footer>
    </>
  );
}
