import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import FileUpload from '../components/FileUpload'
import { jobDescriptionAPI } from '../services/api'

export default function AnalyzePage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [selectedJD, setSelectedJD] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const jdId = searchParams.get('jdId')
    if (jdId) {
      loadJD(jdId)
    }
  }, [searchParams])

  const loadJD = async (jdId) => {
    setLoading(true)
    try {
      const jd = await jobDescriptionAPI.getById(jdId)
      setSelectedJD(jd)
      await jobDescriptionAPI.markUsed(jdId)
    } catch (error) {
      console.error('Error loading JD:', error)
      alert('Không thể tải Job Description')
    } finally {
      setLoading(false)
    }
  }

  const handleSuccess = (data) => {
    navigate('/result', { state: { resumeData: data } })
  }

  return (
    <div className="container" style={{ maxWidth: '800px' }}>
      <h1 className="text-center mb-4 fw-bold">Phân tích CV của bạn</h1>
      {loading ? (
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Đang tải...</span>
          </div>
        </div>
      ) : (
        <FileUpload onUploadSuccess={handleSuccess} selectedJD={selectedJD} />
      )}
    </div>
  )
}