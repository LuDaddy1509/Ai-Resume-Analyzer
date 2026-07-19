import { useNavigate } from 'react-router-dom';

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="text-center py-5">
      <h1 className="display-4 fw-bold text-primary mb-3">AI Resume Analyzer</h1>
      <p className="lead text-muted mb-5">
        Phân tích CV thông minh • Trích xuất kỹ năng • Tối ưu ATS
      </p>

      <div className="row justify-content-center g-4 mb-5">
        <div className="col-md-3">
          <div className="card border-0 shadow-sm h-100">
            <div className="card-body py-4">
              <div className="fs-1 mb-2">📤</div>
              <h5 className="fw-bold">Upload PDF</h5>
              <p className="text-muted small">Tải lên CV dạng PDF của bạn</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card border-0 shadow-sm h-100">
            <div className="card-body py-4">
              <div className="fs-1 mb-2">🤖</div>
              <h5 className="fw-bold">AI Phân tích</h5>
              <p className="text-muted small">Trích xuất thông tin tự động</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card border-0 shadow-sm h-100">
            <div className="card-body py-4">
              <div className="fs-1 mb-2">📊</div>
              <h5 className="fw-bold">Xem kết quả</h5>
              <p className="text-muted small">Kỹ năng, kinh nghiệm, điểm match</p>
            </div>
          </div>
        </div>
      </div>

      <button
        className="btn btn-primary btn-lg px-5"
        onClick={() => navigate('/analyze')}
      >
        🚀 Bắt đầu phân tích CV
      </button>
    </div>
  );
}
