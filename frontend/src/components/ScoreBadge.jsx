export default function ScoreBadge({ score, label }) {
  let className = 'score-badge score-badge';
  if (score >= 80) className += '--strong';
  else if (score >= 60) className += '--good';
  else if (score >= 40) className += '--moderate';
  else className += '--weak';

  const textLabel = label || (
    score >= 80 ? 'Strong' :
    score >= 60 ? 'Good' :
    score >= 40 ? 'Moderate' : 'Weak'
  );

  return (
    <span className={className}>
      <strong>{score ?? '—'}</strong>
      <span>{textLabel}</span>
    </span>
  );
}
