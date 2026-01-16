/**
 * Project detail page - shows project info and allows adding members.
 */

import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { projectsAPI } from '../api';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import { useToast } from '../context/ToastContext';  // ADD at top
import LoadingSpinner from '../components/LoadingSpinner';

const ProjectDetail = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { showToast } = useToast();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showModal, setShowModal] = useState(false);
  
  // Add member form state
  const [newMember, setNewMember] = useState({
    email: '',
    role: 'member'
  });

  useEffect(() => {
    fetchProject();
  }, [projectId]);

  const fetchProject = async () => {
    try {
      setLoading(true);
      const data = await projectsAPI.getProject(projectId);
      setProject(data);
    } catch (err) {
      setError('Failed to load project');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddMember = async (e) => {
  e.preventDefault();
  setError('');
  setSuccess('');
  
  try {
    await projectsAPI.addMember(projectId, newMember);
    showToast(`Successfully added ${newMember.email} to the project!`, 'success');  // ADD THIS
    setShowModal(false);
    setNewMember({ email: '', role: 'member' });
    fetchProject();
  } catch (err) {
    const errorMsg = err.response?.data?.detail || 'Failed to add member';
    setError(errorMsg);
    showToast(errorMsg, 'error');  // ADD THIS
  }
};

  // Check if current user is maintainer
  const isMaintainer = project?.members?.find(
    m => m.user.id === user.id && m.role === 'maintainer'
  );

  if (loading) {
  return (
    <>
      <Navbar />
      <div className="container">
        <LoadingSpinner />  {/* Changed from text */}
      </div>
    </>
  );
}

  if (!project) {
    return (
      <>
        <Navbar />
        <div className="container">
          <div className="error">Project not found</div>
        </div>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <div className="container">
        <button 
          onClick={() => navigate('/projects')}
          className="btn btn-secondary mb-2"
        >
          ← Back to Projects
        </button>

        {error && <div className="error">{error}</div>}
        {success && <div className="success">{success}</div>}

        {/* Project Info Card */}
        <div className="card">
          <div className="flex justify-between items-center mb-2">
            <div>
              <h2>{project.name}</h2>
              <p style={{ color: '#6b7280' }}>Key: {project.key}</p>
            </div>
            <button 
              onClick={() => navigate(`/projects/${projectId}/issues`)}
              className="btn btn-primary"
            >
              View Issues →
            </button>
          </div>
          
          <p style={{ marginTop: '1rem' }}>
            {project.description || 'No description'}
          </p>
        </div>

        {/* Members Section */}
        <div className="card mt-3">
          <div className="flex justify-between items-center mb-3">
            <h3>Team Members ({project.members?.length || 0})</h3>
            {isMaintainer && (
              <button 
                onClick={() => setShowModal(true)}
                className="btn btn-primary"
              >
                + Add Member
              </button>
            )}
          </div>

          {project.members && project.members.length > 0 ? (
            <div style={{ display: 'grid', gap: '1rem' }}>
              {project.members.map((member) => (
                <div 
                  key={member.user.id}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '1rem',
                    border: '1px solid #e5e7eb',
                    borderRadius: '4px'
                  }}
                >
                  <div>
                    <strong>{member.user.name}</strong>
                    <p style={{ color: '#6b7280', fontSize: '0.9rem', margin: '0.25rem 0 0 0' }}>
                      {member.user.email}
                    </p>
                  </div>
                  <span 
                    className={`badge ${member.role === 'maintainer' ? 'badge-high' : 'badge-medium'}`}
                  >
                    {member.role}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#6b7280', textAlign: 'center' }}>No members yet</p>
          )}
        </div>

        {/* Add Member Modal */}
        {showModal && (
          <div className="modal-overlay" onClick={() => setShowModal(false)}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
              <h3>Add Team Member</h3>
              <p style={{ color: '#6b7280', fontSize: '0.9rem', marginBottom: '1rem' }}>
                Add an existing user to this project by their email address.
              </p>
              
              <form onSubmit={handleAddMember}>
                <div className="form-group">
                  <label>Email Address *</label>
                  <input
                    type="email"
                    className="form-control"
                    value={newMember.email}
                    onChange={(e) => setNewMember({...newMember, email: e.target.value})}
                    required
                    placeholder="user@example.com"
                  />
                  <small style={{ color: '#6b7280' }}>
                    User must have an existing account
                  </small>
                </div>

                <div className="form-group">
                  <label>Role *</label>
                  <select
                    className="form-control"
                    value={newMember.role}
                    onChange={(e) => setNewMember({...newMember, role: e.target.value})}
                  >
                    <option value="member">Member</option>
                    <option value="maintainer">Maintainer</option>
                  </select>
                  <small style={{ color: '#6b7280' }}>
                    • Member: Can create issues and comment<br />
                    • Maintainer: Full project control
                  </small>
                </div>

                <div className="flex gap-2 mt-3">
                  <button type="submit" className="btn btn-primary">
                    Add Member
                  </button>
                  <button 
                    type="button" 
                    className="btn btn-secondary"
                    onClick={() => setShowModal(false)}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default ProjectDetail;