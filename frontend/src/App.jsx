import { Suspense, lazy } from 'react';
import { Routes, Route } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';
import PageLoader from './components/PageLoader';
import ProtectedRoute from './components/ProtectedRoute';
import AppShell from './components/AppShell';

// Public pages
const HomePage = lazy(() => import('./pages/HomePage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));

// Protected pages
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const ResumeImportPage = lazy(() => import('./pages/ResumeImportPage'));
const ResumeDetailPage = lazy(() => import('./pages/ResumeDetailPage'));
const AnalyzePage = lazy(() => import('./pages/AnalyzePage'));
const ResultPage = lazy(() => import('./pages/ResultPage'));
const AnalysisHistoryPage = lazy(() => import('./pages/AnalysisHistoryPage'));
const ResumeOptimizationPage = lazy(() => import('./pages/ResumeOptimizationPage'));
const SkillGapsPage = lazy(() => import('./pages/SkillGapsPage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));

// Utility pages
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'));

// Legacy pages (kept but not redesigned)
const JobDescriptionsPage = lazy(() => import('./pages/JobDescriptionsPage'));
const JobDescriptionFormPage = lazy(() => import('./pages/JobDescriptionFormPage'));

function SuspenseWrapper({ children }) {
  return (
    <Suspense
      fallback={
        <div style={{ padding: 'var(--space-8)', maxWidth: 'var(--container-max)', margin: '0 auto' }}>
          <PageLoader />
        </div>
      }
    >
      {children}
    </Suspense>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <SuspenseWrapper>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected routes — wrapped in AppShell */}
          <Route
            element={
              <ProtectedRoute>
                <AppShell />
              </ProtectedRoute>
            }
          >
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/resumes/import" element={<ResumeImportPage />} />
            <Route path="/resumes/:resumeId" element={<ResumeDetailPage />} />
            <Route path="/analyze" element={<AnalyzePage />} />
            <Route path="/result" element={<ResultPage />} />
            <Route path="/analysis-history" element={<AnalysisHistoryPage />} />
            <Route path="/resume-optimization" element={<ResumeOptimizationPage />} />
            <Route path="/skill-gaps" element={<SkillGapsPage />} />
            <Route path="/settings" element={<SettingsPage />} />

            {/* Legacy routes */}
            <Route path="/job-descriptions" element={<JobDescriptionsPage />} />
            <Route path="/job-descriptions/new" element={<JobDescriptionFormPage />} />
            <Route path="/job-descriptions/:id" element={<JobDescriptionFormPage />} />
            <Route path="/job-descriptions/:id/edit" element={<JobDescriptionFormPage />} />
          </Route>

          {/* 404 */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </SuspenseWrapper>
    </ErrorBoundary>
  );
}
