import { useState } from 'react';
import FileUpload from './components/FileUpload';
import SkillsRadar from './components/SkillsRadar';

function App() {
  const [resumeData, setResumeData] = useState(null);

  return (
    <div className="App">
      <h1>AI Resume Analyzer</h1>
      <FileUpload onUploadSuccess={setResumeData} />

      {resumeData && (
        <div>
          <h2>Kết quả phân tích</h2>
          <pre>{JSON.stringify(resumeData, null, 2)}</pre>
          {/* Thêm SkillsRadar, ScoreCard... */}
        </div>
      )}
    </div>
  );
}

export default App;