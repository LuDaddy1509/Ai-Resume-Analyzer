import { useLocation, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import axios from 'axios';
import ScoreCard from '../components/ScoreCard';
import SkillsRadar from '../components/SkillsRadar';
import SuggestionList from '../components/SuggestionList';

export default function ResultPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const resumeData = location.state?.resumeData;
  const [exporting, setExporting] = useState(false);

  const handleExportPDF = async () => {
    if (!resumeData?.history_id) {
      alert('Không thể xuất PDF: Thiếu thông tin lịch sử');
      return;
    }

    setExporting(true);
    try {
      const response = await axios.get(
        `http://127.0.0.1:8000/api/history/${resumeData.history_id}/export/pdf`,
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = `resume-analysis-${resumeData.full_name || 'report'}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export error:', error);
      alert('Không thể xuất PDF. Vui lòng thử lại.');
    } finally {
      setExporting(false);
    }
  };

  const handleExportExcel = async () => {
    if (!resumeData?.history_id) {
      alert('Không thể xuất Excel: Thiếu thông tin lịch sử');
      return;
    }

    setExporting(true);
    try {
      const response = await axios.get(
        `http://127.0.0.1:8000/api/history/${resumeData.history_id}/export/excel`,
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = `resume-analysis-${resumeData.full_name || 'report'}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export error:', error);
      alert('Không thể xuất Excel. Vui lòng thử lại.');
    } finally {
      setExporting(false);
    }
  };

  if (!resumeData) {
    return (
      <div className="text-center mt-5">
        <h4 className="text-muted">Không có dữ liệu. Vui lòng phân tích CV trước.</h4>
        <button className="btn btn-primary mt-3" onClick={() => navigate('/analyze')}>
          ← Quay lại phân tích
        </button>
      </div>
    );
  }

  const hasAnalysis = !!resumeData.analysis;

  return (
    <div className="row justify-content-center">
      <div className="col-md-8">

        {/* Header */}
        <div className="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-3 mb-4">
          <h2 className="fw-bold mb-0">Kết quả phân tích CV</h2>
          <div className="d-flex flex-wrap gap-2">
            <button
              className="btn btn-danger"
              onClick={handleExportPDF}
              disabled={exporting}
            >
              {exporting ? 'Đang xuất...' : 'Xuất PDF'}
            </button>
            <button
              className="btn btn-success"
              onClick={handleExportExcel}
              disabled={exporting}
            >
              {exporting ? 'Đang xuất...' : 'Xuất Excel'}
            </button>
            <button className="btn btn-outline-primary" onClick={() => navigate('/analyze')}>
              Phân tích CV khác
            </button>
          </div>
        </div>

        {/* 1. Điểm match_score & ATS Score */}
        {hasAnalysis && (
          <div className="row g-4 mb-4">
            <div className={resumeData.analysis.ats_score !== undefined && resumeData.analysis.ats_score !== null ? "col-md-6" : "col-12"}>
              <ScoreCard score={resumeData.analysis.match_score} />
            </div>
            {resumeData.analysis.ats_score !== undefined && resumeData.analysis.ats_score !== null && (
              <div className="col-md-6">
                <div className="card shadow h-100 text-center border-0 overflow-hidden">
                  <div className="card-header bg-dark text-white fw-bold py-3 text-uppercase small">
                    🤖 Điểm tối ưu ATS (ATS Score)
                  </div>
                  <div className="card-body d-flex flex-column justify-content-center py-4" style={{ background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)' }}>
                    <h1 className="display-1 fw-bold text-primary mb-2">
                      {resumeData.analysis.ats_score}%
                    </h1>
                    <p className="text-muted fs-5 mb-0">
                      Khả năng vượt qua bộ lọc CV tự động
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Điểm mạnh nổi bật (Strengths) */}
        {hasAnalysis && resumeData.analysis.strengths && resumeData.analysis.strengths.length > 0 && (
          <div className="card shadow mb-4 border-0">
            <div className="card-header bg-success text-white fw-bold py-3">
              🌟 Điểm mạnh nổi bật từ AI
            </div>
            <div className="card-body">
              <ul className="mb-0 ps-3">
                {resumeData.analysis.strengths.map((str, idx) => (
                  <li key={idx} className="mb-2 fs-6">{str}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* 2. Đề xuất tối ưu */}
        {hasAnalysis && (
          <SuggestionList suggestions={resumeData.analysis.suggestions} />
        )}

        {/* 3. Phân tích Kỹ năng so khớp */}
        {hasAnalysis && (
          <SkillsRadar
            matchedSkills={resumeData.analysis.matched_skills}
            missingSkills={resumeData.analysis.missing_skills}
          />
        )}

        {/* Thông tin cá nhân */}
        <div className="card shadow mb-4">
          <div className="card-header bg-primary text-white fw-bold">
            👤 Thông tin cá nhân
          </div>
          <div className="card-body">
            <p className="mb-1"><strong>Họ tên:</strong> {resumeData.full_name}</p>
            <p className="mb-1"><strong>Email:</strong> {resumeData.email}</p>
            {resumeData.phone && (
              <p className="mb-0"><strong>Điện thoại:</strong> {resumeData.phone}</p>
            )}
          </div>
        </div>

        {/* Kỹ năng tổng quát */}
        {resumeData.skills?.length > 0 && (
          <div className="card shadow mb-4">
            <div className="card-header bg-success text-white fw-bold">
              🛠️ Kỹ năng trích xuất ({resumeData.skills.length})
            </div>
            <div className="card-body">
              {resumeData.skills.map((skill) => (
                <span key={skill} className="badge bg-success me-2 mb-2 fs-6">
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Kinh nghiệm */}
        {resumeData.experiences?.length > 0 && (
          <div className="card shadow mb-4">
            <div className="card-header bg-info text-white fw-bold">
              💼 Kinh nghiệm làm việc
            </div>
            <div className="card-body">
              {resumeData.experiences.map((exp, idx) => (
                <div key={idx} className={idx > 0 ? 'mt-3 pt-3 border-top' : ''}>
                  <h6 className="fw-bold mb-0">{exp.position}</h6>
                  <p className="text-muted mb-1">{exp.company} — {exp.dates}</p>
                  {exp.bullets?.length > 0 && (
                    <ul className="mb-0">
                      {exp.bullets.map((b, i) => <li key={i}>{b}</li>)}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
