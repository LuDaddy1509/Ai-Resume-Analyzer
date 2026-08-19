import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FileText, User, Mail, Lock, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';

export default function RegisterPage() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const toast = useToast();

  const [form, setForm] = useState({
    full_name: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeTerms: false,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const updateField = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: '', form: '' }));
  };

  const validate = () => {
    const newErrors = {};
    if (!form.full_name.trim()) newErrors.full_name = 'Full name is required.';
    if (!form.email.trim()) newErrors.email = 'Email is required.';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) newErrors.email = 'Invalid email format.';
    if (!form.password) newErrors.password = 'Password is required.';
    else if (form.password.length < 6) newErrors.password = 'Password must be at least 6 characters.';
    if (form.password !== form.confirmPassword) newErrors.confirmPassword = 'Passwords do not match.';
    if (!form.agreeTerms) newErrors.agreeTerms = 'You must accept the terms.';
    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setLoading(true);
    setErrors({});

    try {
      await register({
        full_name: form.full_name,
        email: form.email,
        password: form.password,
      });
      toast.success('Registration successful', 'Please sign in with your new account.');
      navigate('/login');
    } catch (err) {
      setErrors({ form: err.message || 'Registration failed. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-layout">
      <div className="auth-card">
        <Link to="/" className="auth-card__logo">
          <FileText size={28} />
          <span>AI Resume Analyzer</span>
        </Link>

        <h1 className="auth-card__title">Create your account</h1>
        <p className="auth-card__subtitle">Start analyzing your CV with AI</p>

        {errors.form && (
          <div className="alert alert-error mb-5" role="alert">
            <span>{errors.form}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate>
          <div className="form-group">
            <label className="form-label" htmlFor="reg-name">Full name</label>
            <div className="input-group">
              <User size={18} className="input-icon" />
              <input
                id="reg-name"
                type="text"
                className={`form-input${errors.full_name ? ' error' : ''}`}
                placeholder="John Doe"
                value={form.full_name}
                onChange={(e) => updateField('full_name', e.target.value)}
                autoComplete="name"
                autoFocus
                disabled={loading}
              />
            </div>
            {errors.full_name && <div className="form-error">{errors.full_name}</div>}
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-email">Email address</label>
            <div className="input-group">
              <Mail size={18} className="input-icon" />
              <input
                id="reg-email"
                type="email"
                className={`form-input${errors.email ? ' error' : ''}`}
                placeholder="you@example.com"
                value={form.email}
                onChange={(e) => updateField('email', e.target.value)}
                autoComplete="email"
                disabled={loading}
              />
            </div>
            {errors.email && <div className="form-error">{errors.email}</div>}
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-password">Password</label>
            <div className="password-wrapper">
              <div className="input-group">
                <Lock size={18} className="input-icon" />
                <input
                  id="reg-password"
                  type={showPassword ? 'text' : 'password'}
                  className={`form-input${errors.password ? ' error' : ''}`}
                  placeholder="Min. 6 characters"
                  value={form.password}
                  onChange={(e) => updateField('password', e.target.value)}
                  autoComplete="new-password"
                  disabled={loading}
                  style={{ paddingRight: 'var(--space-10)' }}
                />
              </div>
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                tabIndex={-1}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            {errors.password && <div className="form-error">{errors.password}</div>}
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-confirm">Confirm password</label>
            <div className="input-group">
              <Lock size={18} className="input-icon" />
              <input
                id="reg-confirm"
                type={showPassword ? 'text' : 'password'}
                className={`form-input${errors.confirmPassword ? ' error' : ''}`}
                placeholder="Re-enter your password"
                value={form.confirmPassword}
                onChange={(e) => updateField('confirmPassword', e.target.value)}
                autoComplete="new-password"
                disabled={loading}
              />
            </div>
            {errors.confirmPassword && <div className="form-error">{errors.confirmPassword}</div>}
          </div>

          <div className="form-group">
            <label className="checkbox-label" style={{ fontSize: 'var(--text-sm)' }}>
              <input
                type="checkbox"
                checked={form.agreeTerms}
                onChange={(e) => updateField('agreeTerms', e.target.checked)}
              />
              I agree to the Terms of Service and Privacy Policy
            </label>
            {errors.agreeTerms && <div className="form-error">{errors.agreeTerms}</div>}
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-lg"
            style={{ width: '100%' }}
            disabled={loading}
          >
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <div className="auth-card__footer">
          Already have an account?{' '}
          <Link to="/login">Sign in</Link>
        </div>
      </div>
    </div>
  );
}
