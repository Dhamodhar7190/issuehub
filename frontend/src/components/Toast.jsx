/**
 * Toast notification component.
 * Shows temporary success/error/info messages.
 */

import { useEffect } from 'react';

const Toast = ({ message, type = 'info', onClose, duration = 3000 }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const typeStyles = {
    success: {
      backgroundColor: '#10b981',
      icon: '✓'
    },
    error: {
      backgroundColor: '#ef4444',
      icon: '✕'
    },
    info: {
      backgroundColor: '#3b82f6',
      icon: 'ℹ'
    },
    warning: {
      backgroundColor: '#f59e0b',
      icon: '⚠'
    }
  };

  const style = typeStyles[type] || typeStyles.info;

  return (
    <div
      style={{
        position: 'fixed',
        top: '20px',
        right: '20px',
        backgroundColor: style.backgroundColor,
        color: 'white',
        padding: '1rem 1.5rem',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        minWidth: '300px',
        maxWidth: '500px',
        zIndex: 9999,
        animation: 'slideIn 0.3s ease-out'
      }}
    >
      <span style={{ fontSize: '1.5rem' }}>{style.icon}</span>
      <span style={{ flex: 1 }}>{message}</span>
      <button
        onClick={onClose}
        style={{
          background: 'none',
          border: 'none',
          color: 'white',
          fontSize: '1.5rem',
          cursor: 'pointer',
          padding: '0',
          lineHeight: '1'
        }}
      >
        ×
      </button>
      <style>
        {`
          @keyframes slideIn {
            from {
              transform: translateX(100%);
              opacity: 0;
            }
            to {
              transform: translateX(0);
              opacity: 1;
            }
          }
        `}
      </style>
    </div>
  );
};

export default Toast;