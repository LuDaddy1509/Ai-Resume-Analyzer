import React from 'react';

export default function SuggestionList({ suggestions }) {
  if (!suggestions || suggestions.length === 0) return null;

  return (
    <div className="card shadow mb-4">
      <div className="card-header bg-warning text-dark fw-bold">
        💡 Đề xuất tối ưu CV từ AI
      </div>
      <div className="card-body">
        <ul className="list-group list-group-flush">
          {suggestions.map((suggestion, index) => (
            <li key={index} className="list-group-item d-flex align-items-start px-0 border-0 mb-2">
              <span className="me-2 fs-5">💡</span>
              <span className="fs-6">{suggestion}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
