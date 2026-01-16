/**
 * Navigation bar component.
 * Shows user info and logout button.
 */

import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-content">
        <h1>🐛 IssueHub</h1>
        
        <div className="navbar-user">
          <span>Welcome, {user?.name}</span>
          <button 
            onClick={handleLogout}
            className="btn btn-secondary"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;