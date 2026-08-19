import React from 'react';
import { Lightbulb } from 'lucide-react';

const SuggestionList = React.memo(function SuggestionList({ suggestions }) {
  if (!suggestions || suggestions.length === 0) return null;

  return (
    <div className="panel">
      <div className="panel__header panel__header--warning">
        <Lightbulb size={18} />
        <span>AI Suggestions</span>
      </div>
      <div className="panel__body">
        <ul className="panel__list">
          {suggestions.map((suggestion, index) => (
            <li key={index}>
              <span className="panel__list-icon">
                <Lightbulb size={16} color="var(--color-warning)" />
              </span>
              <span>{suggestion}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
});

export default SuggestionList;
