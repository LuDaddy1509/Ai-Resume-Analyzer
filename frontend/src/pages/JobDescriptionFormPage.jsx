import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { jobDescriptionAPI } from '../services/api';

export default function JobDescriptionFormPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = !!id;

  const [formData, setFormData] = useState({
    title: '',
    company: '',
    job_level: '',
    location: '',
    work_type: '',
    source_url: '',
    raw_text: '',
    tags: []
  });

  const [loading, setLoading] = useState(false);
  const [extractedKeywords, setExtractedKeywords] = useState([]);

  useEffect(() => {
    if (isEdit) {
      loadJD();
    }
  }, [id]);

  const loadJD = async () => {
    try {
      const jd = await jobDescriptionAPI.getById(id);
      setFormData({
        title: jd.title || '',
        company: jd.company || '',
        job_level: jd.job_level || '',
        location: jd.location || '',
        work_type: jd.work_type || '',
        source_url: jd.source_url || '',
        raw_text: jd.raw_text || '',
        tags: jd.tags || []
      });
      setExtractedKeywords(jd.extracted_keywords || []);
    } catch (error) {
      alert('Không thể tải Job Description');
      navigate('/job-descriptions');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isEdit) {
        await jobDescriptionAPI.update(id, formData);
      } else {
        await jobDescriptionAPI.create(formData);
      }
      navigate('/job-descriptions');
    } catch (error) {
      alert('Không thể lưu Job Description');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const wordCount = formData.raw_text.split(/\s+/).filter(Boolean).length;

  return (
    <div className="row justify-content-center">
      <div className="col-md-8">
        <h2 className="mb-4">{isEdit ? 'Chỉnh sửa' : 'Tạo mới'} Job Description</h2>

        <form onSubmit={handleSubmit}>
          <div className="card shadow mb-4">
            <div className="card-header bg-primary text-white">
              Thông tin cơ bản
            </div>
            <div className="card-body">
              <div className="mb-3">
                <label className="form-label">Tên vị trí *</label>
                <input
                  type="text"
                  className="form-control"
                  name="title"
                  value={formData.title}
                  onChange={handleChange}
                  required
                  placeholder="VD: Senior Frontend Developer"
                />
              </div>

              <div className="row">
                <div className="col-md-6 mb-3">
                  <label className="form-label">Công ty</label>
                  <input
                    type="text"
                    className="form-control"
                    name="company"
                    value={formData.company}
                    onChange={handleChange}
                    placeholder="VD: ABC Tech Corp"
                  />
                </div>

                <div className="col-md-6 mb-3">
                  <label className="form-label">Cấp bậc</label>
                  <select
                    className="form-select"
                    name="job_level"
                    value={formData.job_level}
                    onChange={handleChange}
                  >
                    <option value="">Chọn cấp bậc</option>
                    <option value="intern">Intern</option>
                    <option value="fresher">Fresher</option>
                    <option value="junior">Junior</option>
                    <option value="mid">Mid-level</option>
                    <option value="senior">Senior</option>
                    <option value="lead">Lead</option>
                    <option value="manager">Manager</option>
                  </select>
                </div>
              </div>

              <div className="row">
                <div className="col-md-6 mb-3">
                  <label className="form-label">Địa điểm</label>
                  <input
                    type="text"
                    className="form-control"
                    name="location"
                    value={formData.location}
                    onChange={handleChange}
                    placeholder="VD: Hồ Chí Minh"
                  />
                </div>

                <div className="col-md-6 mb-3">
                  <label className="form-label">Hình thức làm việc</label>
                  <select
                    className="form-select"
                    name="work_type"
                    value={formData.work_type}
                    onChange={handleChange}
                  >
                    <option value="">Chọn hình thức</option>
                    <option value="onsite">Onsite</option>
                    <option value="remote">Remote</option>
                    <option value="hybrid">Hybrid</option>
                  </select>
                </div>
              </div>

              <div className="mb-3">
                <label className="form-label">Link nguồn</label>
                <input
                  type="url"
                  className="form-control"
                  name="source_url"
                  value={formData.source_url}
                  onChange={handleChange}
                  placeholder="https://..."
                />
              </div>
            </div>
          </div>

          <div className="card shadow mb-4">
            <div className="card-header bg-primary text-white">
              Nội dung Job Description *
            </div>
            <div className="card-body">
              <div className="mb-3">
                <textarea
                  className="form-control"
                  name="raw_text"
                  value={formData.raw_text}
                  onChange={handleChange}
                  rows="15"
                  required
                  placeholder="Dán toàn bộ nội dung job description vào đây..."
                />
                <small className="text-muted">
                  Số từ: {wordCount}
                  {wordCount < 50 && ' (Quá ngắn - nên thêm chi tiết)'}
                </small>
              </div>

              {extractedKeywords.length > 0 && (
                <div className="alert alert-info">
                  <strong>Kỹ năng đã trích xuất:</strong>
                  <div className="mt-2">
                    {extractedKeywords.map((keyword) => (
                      <span key={keyword} className="badge bg-info me-2 mb-1">
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="d-flex justify-content-between mb-5">
            <button
              type="button"
              className="btn btn-outline-secondary"
              onClick={() => navigate('/job-descriptions')}
            >
              Hủy
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Đang lưu...' : isEdit ? 'Cập nhật' : 'Tạo mới'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
