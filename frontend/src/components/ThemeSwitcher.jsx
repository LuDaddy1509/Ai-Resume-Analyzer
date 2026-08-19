import { useState, useRef, useEffect } from 'react';
import { Sun, Moon, Monitor } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

const options = [
  { value: 'light', label: 'Light', Icon: Sun },
  { value: 'dark', label: 'Dark', Icon: Moon },
  { value: 'system', label: 'System', Icon: Monitor },
];

export default function ThemeSwitcher() {
  const { theme, resolvedTheme, setTheme } = useTheme();
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  // Close on click outside
  useEffect(() => {
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const CurrentIcon = resolvedTheme === 'dark' ? Moon : Sun;

  return (
    <div className="theme-switcher" ref={ref}>
      <button
        className="theme-switcher__btn"
        onClick={() => setOpen(!open)}
        aria-label="Change theme"
        aria-expanded={open}
      >
        <CurrentIcon size={18} />
      </button>
      {open && (
        <div className="theme-switcher__dropdown" role="menu">
          {options.map(({ value, label, Icon }) => (
            <button
              key={value}
              className={`theme-switcher__option${theme === value ? ' active' : ''}`}
              role="menuitem"
              onClick={() => {
                setTheme(value);
                setOpen(false);
              }}
            >
              <Icon size={16} />
              {label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
