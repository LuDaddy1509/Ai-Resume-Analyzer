export default function PageLoader() {
  return (
    <div style={{ padding: 'var(--space-6) 0' }} aria-busy="true" aria-live="polite" role="status" aria-label="Loading content">
      <div className="card" style={{ marginBottom: 'var(--space-4)' }}>
        <div className="card-body">
          <div className="skeleton skeleton-title" style={{ marginBottom: 'var(--space-4)' }} />
          <div className="skeleton skeleton-line" style={{ width: '100%' }} />
          <div className="skeleton skeleton-line" style={{ width: '82%' }} />
          <div className="skeleton skeleton-line" style={{ width: '64%' }} />
        </div>
      </div>
      <div className="card">
        <div className="card-body">
          <div className="skeleton skeleton-title" style={{ width: '40%', marginBottom: 'var(--space-4)' }} />
          <div className="skeleton skeleton-line" style={{ width: '90%' }} />
          <div className="skeleton skeleton-line" style={{ width: '75%' }} />
        </div>
      </div>
    </div>
  );
}