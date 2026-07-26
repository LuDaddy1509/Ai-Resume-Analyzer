import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { resumeAPI, jobDescriptionAPI } from "../services/api";

export default function FileUpload({ onUploadSuccess, selectedJD }) {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [useExistingJD, setUseExistingJD] = useState(false);
  const [availableJDs, setAvailableJDs] = useState([]);
  const [selectedJDId, setSelectedJDId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  const [progressText, setProgressText] = useState("");

  useEffect(() => {
    if (selectedJD) {
      setJobDescription(selectedJD.raw_text);
      setUseExistingJD(true);
    }
  }, [selectedJD]);

  useEffect(() => {
    if (useExistingJD && availableJDs.length === 0) {
      loadJDs();
    }
  }, [useExistingJD]);

  const loadJDs = async () => {
    try {
      const jds = await jobDescriptionAPI.getAll({ status: "active" });
      setAvailableJDs(jds);
    } catch (error) {
      console.error("Error loading JDs:", error);
    }
  };

  const handleJDSelect = async (jdId) => {
    setSelectedJDId(jdId);
    if (jdId) {
      try {
        const jd = await jobDescriptionAPI.getById(jdId);
        setJobDescription(jd.raw_text);
        await jobDescriptionAPI.markUsed(jdId);
      } catch (error) {
        console.error("Error loading JD:", error);
        alert("Không thể tải Job Description");
      }
    } else {
      setJobDescription("");
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setProgress(5);
    setProgressText("Đang kết nối và tải file lên...");

    let currentProgress = 5;
    const progressInterval = setInterval(() => {
      currentProgress += Math.floor(Math.random() * 8) + 2;
      if (currentProgress > 95) currentProgress = 95;
      setProgress(currentProgress);

      if (currentProgress < 25) setProgressText("Đang tải file lên máy chủ...");
      else if (currentProgress < 50) setProgressText("Đang trích xuất nội dung văn bản...");
      else if (currentProgress < 75) setProgressText("Đang nhận dạng kỹ năng & kinh nghiệm...");
      else setProgressText("Đang so khớp với Job Description...");
    }, 250);

    try {
      const data = await resumeAPI.parseResume(file, jobDescription);
      clearInterval(progressInterval);
      setProgress(100);
      setProgressText("Phân tích thành công! Đang chuẩn bị hiển thị kết quả...");
      setTimeout(() => onUploadSuccess(data), 600);
    } catch (err) {
      clearInterval(progressInterval);
      setProgress(0);
      let msg = "Lỗi không xác định";
      if (err.response?.data) {
        const d = err.response.data;
        msg = d.message || d.error || d.detail || JSON.stringify(d);
      } else if (err.message) {
        msg = err.message;
      }
      setError(msg);
      setLoading(false);
    }
  };

  return (
    <div className="card shadow">
      <div className="card-body p-5">
        <h4 className="card-title mb-4">📄 Tải lên CV của bạn</h4>

        <div className="mb-4">
          <label className="form-label fw-bold">1. Chọn file CV (PDF, DOCX, TXT)</label>
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            className="form-control form-control-lg"
            onChange={(e) => {
              const selectedFile = e.target.files[0];
              if (selectedFile) {
                if (selectedFile.size > 5 * 1024 * 1024) {
                  setError("Kích thước file vượt quá giới hạn 5MB. Vui lòng chọn file khác.");
                  setFile(null);
                  e.target.value = "";
                  return;
                }
                const ext = selectedFile.name.split(".").pop().toLowerCase();
                if (ext !== "pdf" && ext !== "docx" && ext !== "txt") {
                  setError("Chỉ hỗ trợ file định dạng PDF, DOCX hoặc TXT.");
                  setFile(null);
                  e.target.value = "";
                  return;
                }
                setFile(selectedFile);
                setError(null);
              } else {
                setFile(null);
              }
            }}
          />
          {file && (
            <p className="text-muted small mt-2 mb-0">
              📎 {file.name} ({(file.size / 1024).toFixed(1)} KB)
            </p>
          )}
        </div>

        <div className="mb-4">
          <label className="form-label fw-bold">2. Yêu cầu công việc / Job Description (Tùy chọn)</label>

          <div className="btn-group w-100 mb-3" role="group">
            <button
              type="button"
              className={`btn ${!useExistingJD ? "btn-primary" : "btn-outline-primary"}`}
              onClick={() => {
                setUseExistingJD(false);
                setSelectedJDId("");
                setJobDescription("");
              }}
            >
              Nhập JD mới
            </button>
            <button
              type="button"
              className={`btn ${useExistingJD ? "btn-primary" : "btn-outline-primary"}`}
              onClick={() => setUseExistingJD(true)}
            >
              Chọn JD đã lưu
            </button>
          </div>

          {useExistingJD ? (
            <div className="mb-3">
              <select
                className="form-select"
                value={selectedJDId}
                onChange={(e) => handleJDSelect(e.target.value)}
              >
                <option value="">-- Chọn Job Description --</option>
                {availableJDs.map((jd) => (
                  <option key={jd.id} value={jd.id}>
                    {jd.title} {jd.company && `- ${jd.company}`}
                  </option>
                ))}
              </select>
              <small className="text-muted">
                Không có JD phù hợp?{" "}
                <button
                  type="button"
                  className="btn btn-link btn-sm p-0"
                  onClick={() => navigate("/job-descriptions/new")}
                >
                  Tạo JD mới
                </button>
              </small>
            </div>
          ) : null}

          <textarea
            className="form-control"
            rows="5"
            placeholder="Dán mô tả công việc hoặc các kỹ năng yêu cầu vào đây để tính điểm phù hợp..."
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            disabled={useExistingJD && !selectedJDId}
          />
        </div>

        {error && <div className="alert alert-danger py-2 mb-4">{error}</div>}

        {loading && (
          <div className="mb-4">
            <div className="d-flex justify-content-between mb-1 small fw-bold text-primary">
              <span>{progressText}</span>
              <span>{progress}%</span>
            </div>
            <div className="progress" style={{ height: "12px", borderRadius: "6px" }}>
              <div
                className="progress-bar progress-bar-striped progress-bar-animated bg-primary"
                role="progressbar"
                style={{ width: `${progress}%`, borderRadius: "6px" }}
                aria-valuenow={progress}
                aria-valuemin="0"
                aria-valuemax="100"
              />
            </div>
          </div>
        )}

        <button
          className="btn btn-primary btn-lg w-100"
          onClick={handleUpload}
          disabled={loading || !file}
        >
          {loading ? "Đang phân tích CV..." : "🚀 Phân tích CV ngay"}
        </button>
      </div>
    </div>
  );
}
