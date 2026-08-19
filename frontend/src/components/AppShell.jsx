import { useState } from 'react';
import { Link, useLocation, Outlet, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  Upload,
  Search,
  History,
  Settings,
  LogOut,
  Menu,
  X,
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import ThemeSwitcher from './ThemeSwitcher';

const navItems = [
  { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { label: 'My CVs', path: '/resumes', icon: FileText },
  { label: 'Import CV', path: '/resumes/import', icon: Upload },
  { label: 'Analyze CV', path: '/analyze', icon: Search },
  { label: 'Analysis History', path: '/analysis-history', icon: History },
];

const secondaryItems = [
  { label: 'Settings', path: '/settings', icon: Settings },
];

export default function AppShell() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleNavClick = () => {
    setSidebarOpen(false);
  };

  const initials = user?.full_name
    ? user.full_name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    : '??';

  return (
    <div className="app-shell">
      {/* Mobile overlay */}
      <div
        className={`sidebar-overlay${sidebarOpen ? ' open' : ''}`}
        onClick={() => setSidebarOpen(false)}
        aria-hidden="true"
      />

      {/* Sidebar */}
      <aside className={`sidebar${sidebarOpen ? ' open' : ''}`} aria-label="Sidebar navigation">
        <div className="sidebar__header">
          <Link className="sidebar__logo" to="/dashboard" onClick={handleNavClick}>
            <FileText size={22} />
            <span>Resume Analyzer</span>
          </Link>
        </div>

        <nav className="sidebar__nav">
          <div className="sidebar__section-title">Main</div>
          {navItems.map(({ label, path, icon: Icon }) => {
            const isActive =
              path === '/dashboard'
                ? pathname === '/dashboard'
                : pathname.startsWith(path);
            return (
              <Link
                key={path}
                to={path}
                className={`sidebar__link${isActive ? ' active' : ''}`}
                onClick={handleNavClick}
                aria-current={isActive ? 'page' : undefined}
              >
                <Icon size={20} />
                <span>{label}</span>
              </Link>
            );
          })}

          <div className="sidebar__section-title">Account</div>
          {secondaryItems.map(({ label, path, icon: Icon }) => (
            <Link
              key={path}
              to={path}
              className={`sidebar__link${pathname === path ? ' active' : ''}`}
              onClick={handleNavClick}
            >
              <Icon size={20} />
              <span>{label}</span>
            </Link>
          ))}
          <button className="sidebar__link" onClick={handleLogout} style={{ width: '100%', border: 'none', background: 'none', cursor: 'pointer', textAlign: 'left' }}>
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </nav>

        <div className="sidebar__footer">
          <div className="sidebar__user">
            <div className="sidebar__avatar">{initials}</div>
            <div className="sidebar__user-info">
              <div className="sidebar__user-name">{user?.full_name || 'User'}</div>
              <div className="sidebar__user-email">{user?.email || ''}</div>
            </div>
            <ThemeSwitcher />
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="app-shell__content">
        {/* Mobile topbar */}
        <div className="app-shell__topbar">
          <button
            className="btn btn-icon btn-ghost"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open navigation menu"
          >
            <Menu size={22} />
          </button>
          <Link className="sidebar__logo" to="/dashboard" style={{ fontSize: 'var(--text-base)' }}>
            <FileText size={20} />
            <span>Resume Analyzer</span>
          </Link>
          <ThemeSwitcher />
        </div>

        <main className="app-shell__main" id="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
