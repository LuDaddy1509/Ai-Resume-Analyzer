import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { FileText, Menu, X } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import ThemeSwitcher from './ThemeSwitcher';

export default function Navbar() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  // If authenticated, show "Go to Dashboard" instead of login/register
  return (
    <nav className="public-nav" role="navigation" aria-label="Main navigation">
      <div className="public-nav__inner">
        <Link className="public-nav__logo" to="/" onClick={() => setMobileOpen(false)}>
          <FileText size={24} />
          <span>AI Resume Analyzer</span>
        </Link>

        <div className={`public-nav__links${mobileOpen ? ' open' : ''}`}>
          <Link
            className={`public-nav__link${pathname === '/' ? ' active' : ''}`}
            to="/"
            onClick={() => setMobileOpen(false)}
          >
            Home
          </Link>
          <a
            className="public-nav__link"
            href="#features"
            onClick={() => setMobileOpen(false)}
          >
            Features
          </a>
        </div>

        <div className="public-nav__actions">
          <ThemeSwitcher />
          {isAuthenticated ? (
            <button
              className="btn btn-primary btn-sm"
              onClick={() => navigate('/dashboard')}
            >
              Dashboard
            </button>
          ) : (
            <>
              <button
                className="btn btn-ghost btn-sm"
                onClick={() => navigate('/login')}
              >
                Log In
              </button>
              <button
                className="btn btn-primary btn-sm"
                onClick={() => navigate('/register')}
              >
                Get Started
              </button>
            </>
          )}
          <button
            className="nav-toggle"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle navigation menu"
            aria-expanded={mobileOpen}
          >
            {mobileOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>
    </nav>
  );
}