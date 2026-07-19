import { Link, useLocation } from 'react-router-dom';

export default function Navbar() {
  const { pathname } = useLocation();

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-primary">
      <div className="container">
        <Link className="navbar-brand fw-bold fs-4" to="/">
          🤖 AI Resume Analyzer
        </Link>
        <div className="navbar-nav ms-auto">
          <Link
            to="/"
            className={`nav-link ${pathname === '/' ? 'active fw-bold' : ''}`}
          >
            Trang chủ
          </Link>
          <Link
            to="/analyze"
            className={`nav-link ${pathname === '/analyze' ? 'active fw-bold' : ''}`}
          >
            Phân tích CV
          </Link>
          <Link
            to="/job-descriptions"
            className={`nav-link ${pathname.startsWith('/job-descriptions') ? 'active fw-bold' : ''}`}
          >
            Job Descriptions
          </Link>
          <Link
            to="/dashboard"
            className={`nav-link ${pathname === '/dashboard' ? 'active fw-bold' : ''}`}
          >
            Dashboard
          </Link>
        </div>
      </div>
    </nav>
  );
}
