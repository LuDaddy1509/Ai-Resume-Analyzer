import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';

const SkillsRadar = React.memo(function SkillsRadar({ matchedSkills = [], missingSkills = [] }) {
  const hasData = matchedSkills.length > 0 || missingSkills.length > 0;

  if (!hasData) {
    return (
      <div className="panel">
        <div className="panel__header panel__header--info">
          <AlertCircle size={18} />
          <span>Skill Analysis</span>
        </div>
        <div className="panel__body" style={{ textAlign: 'center', padding: 'var(--space-10)' }}>
          <p className="text-muted">No required skills data available. Provide a job description to analyze skill matching.</p>
        </div>
      </div>
    );
  }

  const data = [
    { name: 'Matched Skills', value: matchedSkills.length },
    { name: 'Missing Skills', value: missingSkills.length },
  ];

  const COLORS = ['var(--color-success)', 'var(--color-error)'];

  return (
    <div className="panel">
      <div className="panel__header panel__header--info">
        <AlertCircle size={18} />
        <span>Skill Analysis</span>
      </div>
      <div className="panel__body">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-6)', alignItems: 'center' }}>
          <div style={{ height: 220 }}>
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
                    <Cell key={`cell-${index}`} fill={COLORS[index]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend verticalAlign="bottom" height={36} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div>
            {matchedSkills.length > 0 && (
              <div style={{ marginBottom: 'var(--space-4)' }}>
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle size={16} color="var(--color-success)" />
                  <span className="font-semibold text-sm">Matched ({matchedSkills.length})</span>
                </div>
                <div className="flex flex-wrap gap-1">
                  {matchedSkills.map((skill) => (
                    <span key={skill} className="tag tag-primary">{skill}</span>
                  ))}
                </div>
              </div>
            )}
            {missingSkills.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <XCircle size={16} color="var(--color-error)" />
                  <span className="font-semibold text-sm">Missing ({missingSkills.length})</span>
                </div>
                <div className="flex flex-wrap gap-1">
                  {missingSkills.map((skill) => (
                    <span key={skill} className="tag">{skill}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
});

export default SkillsRadar;
