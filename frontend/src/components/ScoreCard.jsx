import React from 'react';

function getScoreInfo(score) {
  if (score >= 80) return { label: 'Strong', className: '--strong', color: 'var(--color-score-strong)' };
  if (score >= 60) return { label: 'Good', className: '--good', color: 'var(--color-score-good)' };
  if (score >= 40) return { label: 'Moderate', className: '--moderate', color: 'var(--color-score-moderate)' };
  return { label: 'Weak', className: '--weak', color: 'var(--color-score-weak)' };
}

const ScoreCard = React.memo(function ScoreCard({ score, title = 'Score', subtitle }) {
  const { label, color } = getScoreInfo(score ?? 0);
  const numericScore = score ?? 0;

  // SVG circle params
  const size = 140;
  const strokeWidth = 8;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (numericScore / 100) * circumference;

  return (
    <div className="card">
      <div className="score-display">
        <div className="score-circle">
          <svg viewBox={`0 0 ${size} ${size}`}>
            <circle
              className="score-circle__track"
              cx={size / 2}
              cy={size / 2}
              r={radius}
            />
            <circle
              className="score-circle__fill"
              cx={size / 2}
              cy={size / 2}
              r={radius}
              stroke={color}
              strokeDasharray={circumference}
              strokeDashoffset={offset}
            />
          </svg>
          <span className="score-circle__value" style={{ color }}>
            {numericScore}
          </span>
        </div>
        <div className="score-circle__label" style={{ color }}>
          {label}
        </div>
        <div style={{ marginTop: 'var(--space-3)', fontSize: 'var(--text-lg)', fontWeight: 'var(--weight-semibold)', color: 'var(--color-text)' }}>
          {title}
        </div>
        {subtitle && (
          <div style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)', marginTop: 'var(--space-1)' }}>
            {subtitle}
          </div>
        )}
      </div>
    </div>
  );
});

export default ScoreCard;
