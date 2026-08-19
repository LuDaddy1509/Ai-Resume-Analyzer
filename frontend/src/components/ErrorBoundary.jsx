import { Component } from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

export default class ErrorBoundary extends Component {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  handleReload = () => {
    this.setState({ hasError: false });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="auth-layout" role="alert">
          <div style={{ textAlign: 'center', maxWidth: 480, padding: 'var(--space-8)' }}>
            <div style={{ marginBottom: 'var(--space-6)', color: 'var(--color-warning)' }}>
              <AlertTriangle size={64} />
            </div>
            <h1 style={{ fontSize: 'var(--text-2xl)', fontWeight: 'var(--weight-bold)', marginBottom: 'var(--space-3)', color: 'var(--color-text)' }}>
              Unexpected Error
            </h1>
            <p style={{ color: 'var(--color-text-secondary)', marginBottom: 'var(--space-6)', lineHeight: 'var(--leading-relaxed)' }}>
              The application encountered an unexpected error. Reload the page or return to the home page.
            </p>
            <div className="flex justify-center gap-3">
              <button className="btn btn-primary" onClick={this.handleReload}>
                <RefreshCw size={18} />
                Try Again
              </button>
              <a className="btn btn-secondary" href="/">
                <Home size={18} />
                Home Page
              </a>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}