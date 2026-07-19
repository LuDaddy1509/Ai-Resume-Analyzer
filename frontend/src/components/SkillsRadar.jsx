import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

export default function SkillsRadar({ matchedSkills = [], missingSkills = [] }) {
  const hasData = matchedSkills.length > 0 || missingSkills.length > 0;

  if (!hasData) {
    return (
      <div className="card shadow mb-4">
        <div className="card-header bg-secondary text-white fw-bold">
          🛠️ Phân tích kỹ năng yêu cầu
        </div>
        <div className="card-body text-center py-4">
          <p className="text-muted mb-0">Không có dữ liệu kỹ năng yêu cầu. Hãy dán mô tả công việc (JD) để phân tích kỹ năng.</p>
        </div>
      </div>
    );
  }

  const data = [
    { name: 'Kỹ năng tương thích', value: matchedSkills.length },
    { name: 'Kỹ năng còn thiếu', value: missingSkills.length },
  ];

  const COLORS = ['#28a745', '#dc3545'];

  return (
    <div className="card shadow mb-4">
      <div className="card-header bg-secondary text-white fw-bold">
        🛠️ Phân tích kỹ năng yêu cầu
      </div>
      <div className="card-body">
        <div className="row align-items-center">
          <div className="col-md-6" style={{ height: '220px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend verticalAlign="bottom" height={36} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="col-md-6">
            {matchedSkills.length > 0 && (
              <div className="mb-3">
                <span className="badge bg-success mb-2 d-inline-block">✅ Đã có ({matchedSkills.length})</span>
                <div>
                  {matchedSkills.map((skill) => (
                    <span key={skill} className="badge bg-light text-dark border me-1 mb-1 small">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {missingSkills.length > 0 && (
              <div>
                <span className="badge bg-danger mb-2 d-inline-block">❌ Thiếu ({missingSkills.length})</span>
                <div>
                  {missingSkills.map((skill) => (
                    <span key={skill} className="badge bg-light text-dark border me-1 mb-1 small">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
