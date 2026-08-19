import { AlertTriangle } from 'lucide-react';

export default function ConfirmDialog({ open, title, message, confirmLabel = 'Delete', onConfirm, onCancel }) {
  if (!open) return null;

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal" onClick={(e) => e.stopPropagation()} role="alertdialog" aria-modal="true" aria-labelledby="confirm-title">
        <div className="modal__header">
          <div style={{ width: 44, height: 44, borderRadius: 'var(--radius-full)', background: 'var(--color-error-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            <AlertTriangle size={22} color="var(--color-error)" />
          </div>
          <div>
            <h3 id="confirm-title" style={{ fontSize: 'var(--text-lg)', fontWeight: 'var(--weight-semibold)', color: 'var(--color-text)' }}>
              {title || 'Confirm Action'}
            </h3>
          </div>
        </div>
        <div className="modal__body">
          <p>{message || 'This action cannot be undone. Are you sure you want to continue?'}</p>
        </div>
        <div className="modal__footer">
          <button className="btn btn-secondary" onClick={onCancel}>
            Cancel
          </button>
          <button className="btn btn-danger" onClick={onConfirm}>
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
