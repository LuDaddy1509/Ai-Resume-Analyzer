import { Routes, Route } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import AnalyzePage from './pages/AnalyzePage';
import ResultPage from './pages/ResultPage';
import JobDescriptionsPage from './pages/JobDescriptionsPage';
import JobDescriptionFormPage from './pages/JobDescriptionFormPage';
import DashboardPage from './pages/DashboardPage';

function App() {
  return (
    <>
      <Navbar />
      <div className="container mt-4">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/analyze" element={<AnalyzePage />} />
          <Route path="/result" element={<ResultPage />} />
          <Route path="/job-descriptions" element={<JobDescriptionsPage />} />
          <Route path="/job-descriptions/new" element={<JobDescriptionFormPage />} />
          <Route path="/job-descriptions/:id" element={<JobDescriptionFormPage />} />
          <Route path="/job-descriptions/:id/edit" element={<JobDescriptionFormPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
        </Routes>
      </div>
    </>
  );
}

export default App;
