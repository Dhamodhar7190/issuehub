/**
 * Issues list page - shows all issues in a project with filters.
 */
import { useToast } from '../context/ToastContext';  // ADD at top
import LoadingSpinner from '../components/LoadingSpinner';
import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { issuesAPI, projectsAPI } from '../api';
import Navbar from '../components/Navbar';

const IssuesList = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  
  const [project, setProject] = useState(null);
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const { showToast } = useToast();  
  
  // Filter and sort state
  const [filters, setFilters] = useState({
    q: '',
    status: '',
    priority: '',
    assignee_id: '',
    sort: 'created_at',
    page: 1,
    page_size: 20
  });
  
  // New issue form state
  const [newIssue, setNewIssue] = useState({
    title: '',
    description: '',
    priority: 'medium',
    assignee_id: ''
  });
  
  const [members, setMembers] = useState([]);

  // Fetch project and issues on mount and when filters change
  useEffect(() => {
    fetchProject();
    fetchIssues();
  }, [projectId, filters.q, filters.status, filters.priority, filters.sort]);

  const fetchProject = async () => {
    try {
      const data = await projectsAPI.getProject(projectId);
      setProject(data);
      setMembers(data.members || []);
    } catch (err) {
      setError('Failed to load project');
      console.error(err);
    }
  };

  const fetchIssues = async () => {
  try {
    setLoading(true);
    
    // Create clean params object (remove empty strings)
    const cleanParams = {};
    Object.keys(filters).forEach(key => {
      if (filters[key] !== '' && filters[key] !== null) {
        cleanParams[key] = filters[key];
      }
    });
    
    const data = await issuesAPI.getIssues(projectId, cleanParams);
    setIssues(data.issues);
  } catch (err) {
    setError('Failed to load issues');
    console.error(err);
  } finally {
    setLoading(false);
  }
};

 const handleCreateIssue = async (e) => {
  e.preventDefault();
  
  try {
    await issuesAPI.createIssue(projectId, {
      ...newIssue,
      assignee_id: newIssue.assignee_id || null
    });
    showToast('Issue created successfully!', 'success');  // ADD THIS
    setShowModal(false);
    setNewIssue({ title: '', description: '', priority: 'medium', assignee_id: '' });
    fetchIssues();
  } catch (err) {
    const errorMsg = err.response?.data?.detail || 'Failed to create issue';
    showToast(errorMsg, 'error');  // ADD THIS
  }
};

  const handleFilterChange = (field, value) => {
    setFilters({ ...filters, [field]: value });
  };

  const getStatusBadgeClass = (status) => {
    return `badge badge-${status}`;
  };

  const getPriorityBadgeClass = (priority) => {
    return `badge badge-${priority}`;
  };

  if (loading && !issues.length) {
  return (
    <>
      <Navbar />
      <div className="container">
        <LoadingSpinner />  {/* Changed from text */}
      </div>
    </>
  );
}

  return (
    <>
      <Navbar />
      <div className="container">
        {/* Header */}
        <div className="flex justify-between items-center mb-3">
          <div>
            <button 
              onClick={() => navigate('/projects')}
              className="btn btn-secondary"
              style={{ marginBottom: '0.5rem' }}
            >
              ← Back to Projects
            </button>
            <h2>{project?.name || 'Project'}</h2>
            <p style={{ color: '#6b7280' }}>{project?.description}</p>
          </div>
          <button 
            onClick={() => setShowModal(true)}
            className="btn btn-primary"
          >
            + Create Issue
          </button>
        </div>

        {error && <div className="error">{error}</div>}

        {/* Filters */}
        <div className="filters">
          <input
            type="text"
            placeholder="Search issues..."
            value={filters.q}
            onChange={(e) => handleFilterChange('q', e.target.value)}
            style={{ flex: '1', minWidth: '200px' }}
          />
          
          <select 
            value={filters.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
          >
            <option value="">All Statuses</option>
            <option value="open">Open</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>

          <select 
            value={filters.priority}
            onChange={(e) => handleFilterChange('priority', e.target.value)}
          >
            <option value="">All Priorities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>

          <select 
            value={filters.sort}
            onChange={(e) => handleFilterChange('sort', e.target.value)}
          >
            <option value="created_at">Newest First</option>
            <option value="updated_at">Recently Updated</option>
            <option value="priority">Priority</option>
            <option value="status">Status</option>
          </select>
        </div>

        {/* Issues List */}
        {issues.length === 0 ? (
          <div className="card text-center">
            <p>No issues found. Create your first issue to get started!</p>
          </div>
        ) : (
          <div>
            {issues.map((issue) => (
              <div 
                key={issue.id}
                className="card"
                style={{ cursor: 'pointer' }}
                onClick={() => navigate(`/issues/${issue.id}`)}
              >
                <div className="flex justify-between items-center">
                  <div style={{ flex: 1 }}>
                    <div className="flex items-center gap-2 mb-1">
                      <span className={getStatusBadgeClass(issue.status)}>
                        {issue.status.replace('_', ' ')}
                      </span>
                      <span className={getPriorityBadgeClass(issue.priority)}>
                        {issue.priority}
                      </span>
                    </div>
                    
                    <h3 style={{ marginBottom: '0.5rem' }}>
                      {project?.key}-{issue.id}: {issue.title}
                    </h3>
                    
                    <p style={{ color: '#6b7280', fontSize: '0.9rem' }}>
                      {issue.description?.substring(0, 150)}
                      {issue.description?.length > 150 ? '...' : ''}
                    </p>
                    
                    <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: '#6b7280' }}>
                      Reporter: {issue.reporter.name} • 
                      {issue.assignee ? ` Assignee: ${issue.assignee.name}` : ' Unassigned'}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Create Issue Modal */}
        {showModal && (
          <div className="modal-overlay" onClick={() => setShowModal(false)}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
              <h3>Create New Issue</h3>
              
              <form onSubmit={handleCreateIssue}>
                <div className="form-group">
                  <label>Title *</label>
                  <input
                    type="text"
                    className="form-control"
                    value={newIssue.title}
                    onChange={(e) => setNewIssue({...newIssue, title: e.target.value})}
                    required
                    placeholder="Brief description of the issue"
                  />
                </div>

                <div className="form-group">
                  <label>Description</label>
                  <textarea
                    className="form-control"
                    value={newIssue.description}
                    onChange={(e) => setNewIssue({...newIssue, description: e.target.value})}
                    placeholder="Detailed description, steps to reproduce, etc."
                    rows="5"
                  />
                </div>

                <div className="form-group">
                  <label>Priority *</label>
                  <select
                    className="form-control"
                    value={newIssue.priority}
                    onChange={(e) => setNewIssue({...newIssue, priority: e.target.value})}
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Assignee</label>
                  <select
                    className="form-control"
                    value={newIssue.assignee_id}
                    onChange={(e) => setNewIssue({...newIssue, assignee_id: e.target.value})}
                  >
                    <option value="">Unassigned</option>
                    {members.map((member) => (
                      <option key={member.user.id} value={member.user.id}>
                        {member.user.name} ({member.role})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex gap-2">
                  <button type="submit" className="btn btn-primary">
                    Create Issue
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

export default IssuesList;