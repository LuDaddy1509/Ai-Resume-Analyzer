import React from 'react';

export default function ScoreCard({ score }) {
  // Xác định màu sắc dựa trên điểm số
  const getScoreColor = (val) => {
    if (val >= 80) return 'text-success';
    if (val >= 50) return 'text-warning';
    return 'text-danger';
  };

  const getProgressColorClass = (val) => {
    if (val >= 80) return 'bg-success';
    if (val >= 50) return 'bg-warning';
    return 'bg-danger';
  };

  return (
    <div className="card shadow mb-4">
      <div className="card-header bg-dark text-white fw-bold">
        📊 Điểm tương thích CV (Match Score)
      </div>
      <div className="card-body text-center py-4">
        <h1 className={`display-1 fw-bold ${getScoreColor(score)}`}>
          {score}%
        </h1>
        <p className="text-muted fs-5 mb-3">
          Mức độ phù hợp của CV với yêu cầu công việc
        </p>
        <div className="progress" style={{ height: '25px' }}>
          <div
            className={`progress-bar progress-bar-striped progress-bar-animated ${getProgressColorClass(score)}`}
            role="progressbar"
            style={{ width: `${score}%` }}
            aria-valuenow={score}
            aria-valuemin="0"
            aria-valuemax="100"
          >
            {score}%
          </div>
        </div>
      </div>
    </div>
  );
}
