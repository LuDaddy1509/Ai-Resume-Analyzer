import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { jobDescriptionAPI } from '../services/api';
import useDebounce from '../hooks/useDebounce';
import PageLoader from '../components/PageLoader';

export default function JobDescriptionsPage() {
  const [jds, setJds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search, 300);
  const [statusFilter, setStatusFilter] = useState('active');
  const navigate = useNavigate();

  const loadJDs = useCallback(async () => {
    setLoading(true);
    try {
      const data = await jobDescriptionAPI.getAll({ status: statusFilter, search: debouncedSearch });
      setJds(data);
    } catch (error) {
      console.error('Error loading JDs:', error);
      alert('Không thể tải danh sách Job Descriptions');
    } finally {
      setLoading(false);
    }
  }, [statusFilter, debouncedSearch]);

  useEffect(() => {
    loadJDs();
  }, [loadJDs]);

  const handleDuplicate = async (id) => {
    try {
      await jobDescriptionAPI.duplicate(id);
      loadJDs();
    } catch (error) {
      console.error('Error duplicating JD:', error);
      alert('Không thể sao chép JD');
    }
  };

  const handleArchive = async (id) => {
    if (confirm('Bạn có chắc muốn lưu trữ Job Description này?')) {
      try {
        await jobDescriptionAPI.archive(id);
        loadJDs();
      } catch (error) {
        console.error('Error archiving JD:', error);
        alert('Không thể lưu trữ JD');
      }
    }
  };

  const handleUse = (id) => {
    navigate(`/analyze?jdId=${id}`);
  };

  return (
    <div className="row">
      <div className="col-12">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2 className="fw-bold">Job Descriptions</h2>
          <button className="btn btn-primary" onClick={() => navigate('/job-descriptions/new')}>
            + Tạo JD mới
          </button>
        </div>

        <div className="card shadow mb-4">
          <div className="card-body">
            <div className="row mb-3">
              <div className="col-md-6">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Tìm kiếm theo title, company hoặc nội dung..."
                  aria-label="Tìm kiếm Job Description"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>
              <div className="col-md-3">
                <select
                  className="form-select"
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <option value="">Tất cả trạng thái</option>
                  <option value="active">Active</option>
                  <option value="archived">Archived</option>
                </select>
              </div>
            </div>

            {loading ? (
              <PageLoader rows={4} />
            ) : jds.length === 0 ? (
              <div className="text-center text-muted py-5">
                <p>Chưa có Job Description nào</p>
                <button className="btn btn-primary" onClick={() => navigate('/job-descriptions/new')}>
                  Tạo JD đầu tiên
                </button>
              </div>
            ) : (
              <div className="row">
                {jds.map((jd) => (
                  <div key={jd.id} className="col-md-6 mb-3">
                    <div className="card h-100">
                      <div className="card-body">
                        <h5 className="card-title">{jd.title}</h5>
                        {jd.company && <p className="text-muted mb-2">{jd.company}</p>}
                        <div className="mb-2">
                          {jd.job_level && <span className="badge bg-info me-2">{jd.job_level}</span>}
                          {jd.work_type && <span className="badge bg-secondary me-2">{jd.work_type}</span>}
                          {jd.status === 'archived' && <span className="badge bg-warning">Archived</span>}
                        </div>
                        <p className="small text-muted mb-2">
                          Đã dùng {jd.usage_count} lần
                          {jd.last_used_at && ` • Lần cuối: ${new Date(jd.last_used_at).toLocaleDateString('vi-VN')}`}
                        </p>
                        <div className="btn-group btn-group-sm" role="group">
                          <button
                            className="btn btn-outline-primary"
                            onClick={() => navigate(`/job-descriptions/${jd.id}`)}
                          >
                            Xem
                          </button>
                          <button
                            className="btn btn-outline-success"
                            onClick={() => handleUse(jd.id)}
                          >
                            Sử dụng
                          </button>
                          <button
                            className="btn btn-outline-secondary"
                            onClick={() => navigate(`/job-descriptions/${jd.id}/edit`)}
                          >
                            Sửa
                          </button>
                          <button
                            className="btn btn-outline-info"
                            onClick={() => handleDuplicate(jd.id)}
                          >
                            Sao chép
                          </button>
                          {jd.status === 'active' && (
                            <button
                              className="btn btn-outline-warning"
                              onClick={() => handleArchive(jd.id)}
                            >
                              Lưu trữ
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
