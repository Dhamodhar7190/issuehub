/**
 * Loading spinner component for better visual feedback.
 */

const LoadingSpinner = ({ size = 'medium', color = '#2563eb', inline = false }) => {
  const sizes = {
    small: '20px',
    medium: '40px',
    large: '60px'
  };

  const spinnerStyle = {
    width: sizes[size],
    height: sizes[size],
    border: `4px solid rgba(37, 99, 235, 0.1)`,
    borderTop: `4px solid ${color}`,
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    margin: inline ? '0' : '0 auto', // No auto margin if inline
    display: inline ? 'inline-block' : 'block' // inline-block for buttons
  };

  const containerStyle = inline 
    ? { display: 'inline-flex', alignItems: 'center', justifyContent: 'center' }
    : { textAlign: 'center', padding: '2rem' };

  return (
    <div style={containerStyle}>
      <div style={spinnerStyle}></div>
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
};

export default LoadingSpinner;