import { Link } from 'react-router-dom';
import { FileQuestion, Home, ArrowLeft } from 'lucide-react';

export default function NotFoundPage() {
  return (
    <div className="auth-layout">
      <div style={{ textAlign: 'center', maxWidth: 480, padding: 'var(--space-8)' }}>
        <div style={{ marginBottom: 'var(--space-5)', color: 'var(--color-text-muted)' }}>
          <FileQuestion size={72} strokeWidth={1.5} />
        </div>
        <h1 style={{ fontSize: 'var(--text-5xl)', fontWeight: 'var(--weight-extrabold)', color: 'var(--color-primary)', marginBottom: 'var(--space-3)' }}>
          404
        </h1>
        <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: 'var(--weight-semibold)', color: 'var(--color-text)', marginBottom: 'var(--space-3)' }}>
          Page not found
        </h2>
        <p style={{ color: 'var(--color-text-secondary)', marginBottom: 'var(--space-8)', lineHeight: 'var(--leading-relaxed)' }}>
          The page you are looking for does not exist or has been moved. Check the URL or navigate back.
        </p>
        <div className="flex justify-center gap-3">
          <Link to="/" className="btn btn-primary">
            <Home size={18} />
            Home Page
          </Link>
          <button className="btn btn-secondary" onClick={() => window.history.back()}>
            <ArrowLeft size={18} />
            Go Back
          </button>
        </div>
      </div>
    </div>
  );
}
