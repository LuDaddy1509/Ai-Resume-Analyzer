import { useState, useRef, useCallback } from 'react';
import { Upload, FileText, X } from 'lucide-react';

export default function FileDropZone({ onFileSelect, accept = '.pdf,.docx', maxSizeMB = 10, file, onClear }) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef(null);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      e.stopPropagation();
      setDragging(false);

      const droppedFile = e.dataTransfer?.files?.[0];
      if (droppedFile) {
        onFileSelect(droppedFile);
      }
    },
    [onFileSelect]
  );

  const handleClick = () => {
    inputRef.current?.click();
  };

  const handleChange = (e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      onFileSelect(selectedFile);
    }
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (file) {
    return (
      <div className="dropzone has-file" style={{ padding: 'var(--space-6) var(--space-8)' }}>
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <FileText size={36} color="var(--color-success)" />
            <div style={{ textAlign: 'left' }}>
              <div style={{ fontWeight: 'var(--weight-semibold)', color: 'var(--color-text)', fontSize: 'var(--text-base)' }}>
                {file.name}
              </div>
              <div style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)' }}>
                {formatSize(file.size)}
              </div>
            </div>
          </div>
          {onClear && (
            <button className="btn btn-icon btn-ghost" onClick={onClear} aria-label="Remove file">
              <X size={20} />
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div
      className={`dropzone${dragging ? ' active' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') handleClick();
      }}
      aria-label="Drop a file or click to browse"
    >
      <div className="dropzone__icon">
        <Upload size={40} />
      </div>
      <div className="dropzone__title">
        Drop your CV here or click to browse
      </div>
      <div className="dropzone__subtitle">
        Accepted formats: {accept.replace(/\./g, '').toUpperCase().replace(/,/g, ', ')} • Max {maxSizeMB}MB
      </div>
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        onChange={handleChange}
        style={{ display: 'none' }}
        aria-hidden="true"
      />
    </div>
  );
}
