import { Settings as SettingsIcon } from 'lucide-react';
import ThemeSwitcher from '../components/ThemeSwitcher';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';

export default function SettingsPage() {
  const { user } = useAuth();
  const { theme } = useTheme();

  return (
    <div>
      <div className="page-header">
        <h1 className="page-header__title">Settings</h1>
        <p className="page-header__subtitle">Manage your account preferences</p>
      </div>

      {/* Profile */}
      <div className="card mb-6">
        <div className="card-header flex items-center gap-2">
          <SettingsIcon size={18} />
          Profile
        </div>
        <div className="card-body">
          <div className="grid-2">
            <div>
              <div className="text-sm text-muted mb-1">Full Name</div>
              <div className="font-medium">{user?.full_name || '—'}</div>
            </div>
            <div>
              <div className="text-sm text-muted mb-1">Email</div>
              <div className="font-medium">{user?.email || '—'}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Theme */}
      <div className="card">
        <div className="card-header">Appearance</div>
        <div className="card-body">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">Theme</div>
              <div className="text-sm text-muted mt-1">
                Current: {theme.charAt(0).toUpperCase() + theme.slice(1)}
              </div>
            </div>
            <ThemeSwitcher />
          </div>
        </div>
      </div>
    </div>
  );
}
