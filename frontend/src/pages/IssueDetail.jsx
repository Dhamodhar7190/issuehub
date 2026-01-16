/**
 * Issue detail page - shows full issue info with comments.
 */

import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { issuesAPI, commentsAPI, projectsAPI } from '../api';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import { useToast } from '../context/ToastContext';  // ADD at top
import LoadingSpinner from '../components/LoadingSpinner';  // ADD at top

const IssueDetail = () => {
    const { showToast } = useToast();
  const { issueId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [issue, setIssue] = useState(null);
  const [comments, setComments] = useState([]);
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Comment form state
  const [newComment, setNewComment] = useState('');
  const [submittingComment, setSubmittingComment] = useState(false);
  
  // Edit mode state
  const [editMode, setEditMode] = useState(false);
  const [editData, setEditData] = useState({
    title: '',
    description: '',
    status: '',
    priority: '',
    assignee_id: ''
  });

  useEffect(() => {
    fetchIssue();
    fetchComments();
  }, [issueId]);

  const fetchIssue = async () => {
    try {
      setLoading(true);
      const data = await issuesAPI.getIssue(issueId);
      setIssue(data);
      
      // Fetch project members for assignee dropdown
      const projectData = await projectsAPI.getProject(data.project_id);
      setMembers(projectData.members || []);
      
      // Initialize edit form
      setEditData({
        title: data.title,
        description: data.description || '',
        status: data.status,
        priority: data.priority,
        assignee_id: data.assignee?.id || ''
      });
    } catch (err) {
      setError('Failed to load issue');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchComments = async () => {
    try {
      const data = await commentsAPI.getComments(issueId);
      setComments(data);
    } catch (err) {
      console.error('Failed to load comments:', err);
    }
  };

  const handleAddComment = async (e) => {
  e.preventDefault();
  
  if (!newComment.trim()) return;
  
  try {
    setSubmittingComment(true);
    await commentsAPI.createComment(issueId, { body: newComment });
    showToast('Comment added successfully!', 'success');  // ADD THIS
    setNewComment('');
    fetchComments();
  } catch {
    showToast('Failed to add comment', 'error');  // ADD THIS
  } finally {
    setSubmittingComment(false);
  }
};

const handleUpdateIssue = async (e) => {
  e.preventDefault();
  
  try {
    await issuesAPI.updateIssue(issueId, {
      ...editData,
      assignee_id: editData.assignee_id || null
    });
    showToast('Issue updated successfully!', 'success');  // ADD THIS
    setEditMode(false);
    fetchIssue();
  } catch (err) {
    const errorMsg = err.response?.data?.detail || 'Failed to update issue';
    showToast(errorMsg, 'error');  // ADD THIS
  }
};

const handleDeleteIssue = async () => {
  if (!window.confirm('Are you sure you want to delete this issue?')) {
    return;
  }
  
  try {
    await issuesAPI.deleteIssue(issueId);
    showToast('Issue deleted successfully', 'success');  // ADD THIS
    navigate(`/projects/${issue.project_id}/issues`);
  } catch (err) {
    const errorMsg = err.response?.data?.detail || 'Failed to delete issue';
    showToast(errorMsg, 'error');  // ADD THIS
  }
};



  const getStatusBadgeClass = (status) => `badge badge-${status}`;
  const getPriorityBadgeClass = (priority) => `badge badge-${priority}`;

  const canEdit = issue && (
    user.id === issue.reporter.id || 
    members.find(m => m.user.id === user.id && m.role === 'maintainer')
  );

  const canDelete = issue && members.find(m => m.user.id === user.id && m.role === 'maintainer');

 // Replace loading section:
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

  if (!issue) {
    return (
      <>
        <Navbar />
        <div className="container">
          <div className="error">Issue not found</div>
        </div>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <div className="container">
        <button 
          onClick={() => navigate(`/projects/${issue.project_id}/issues`)}
          className="btn btn-secondary mb-2"
        >
          ← Back to Issues
        </button>

        {error && <div className="error">{error}</div>}

        <div className="card">
          {/* Issue Header */}
          {!editMode ? (
            <>
              <div className="flex justify-between items-center mb-2">
                <div className="flex items-center gap-2">
                  <span className={getStatusBadgeClass(issue.status)}>
                    {issue.status.replace('_', ' ')}
                  </span>
                  <span className={getPriorityBadgeClass(issue.priority)}>
                    {issue.priority}
                  </span>
                </div>
                
                <div className="flex gap-2">
                  {canEdit && (
                    <button 
                      onClick={() => setEditMode(true)}
                      className="btn btn-primary"
                    >
                      Edit
                    </button>
                  )}
                  {canDelete && (
                    <button 
                      onClick={handleDeleteIssue}
                      className="btn btn-danger"
                    >
                      Delete
                    </button>
                  )}
                </div>
              </div>

              <h2>{issue.title}</h2>
              
              <div style={{ marginTop: '1rem', color: '#6b7280', fontSize: '0.9rem' }}>
                <div>Reporter: <strong>{issue.reporter.name}</strong></div>
                <div>
                  Assignee: <strong>{issue.assignee?.name || 'Unassigned'}</strong>
                </div>
                <div>
                  Created: {new Date(issue.created_at).toLocaleString()}
                </div>
                <div>
                  Updated: {new Date(issue.updated_at).toLocaleString()}
                </div>
              </div>

              <div style={{ marginTop: '1.5rem', whiteSpace: 'pre-wrap' }}>
                {issue.description || 'No description provided.'}
              </div>
            </>
          ) : (
            /* Edit Form */
            <form onSubmit={handleUpdateIssue}>
              <div className="form-group">
                <label>Title *</label>
                <input
                  type="text"
                  className="form-control"
                  value={editData.title}
                  onChange={(e) => setEditData({...editData, title: e.target.value})}
                  required
                />
              </div>

              <div className="form-group">
                <label>Description</label>
                <textarea
                  className="form-control"
                  value={editData.description}
                  onChange={(e) => setEditData({...editData, description: e.target.value})}
                  rows="5"
                />
              </div>

              <div className="form-group">
                <label>Status *</label>
                <select
                  className="form-control"
                  value={editData.status}
                  onChange={(e) => setEditData({...editData, status: e.target.value})}
                >
                  <option value="open">Open</option>
                  <option value="in_progress">In Progress</option>
                  <option value="resolved">Resolved</option>
                  <option value="closed">Closed</option>
                </select>
              </div>

              <div className="form-group">
                <label>Priority *</label>
                <select
                  className="form-control"
                  value={editData.priority}
                  onChange={(e) => setEditData({...editData, priority: e.target.value})}
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
                  value={editData.assignee_id}
                  onChange={(e) => setEditData({...editData, assignee_id: e.target.value})}
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
                <button type="submit" className="btn btn-success">
                  Save Changes
                </button>
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={() => setEditMode(false)}
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
        </div>

        {/* Comments Section */}
        <div className="card mt-3">
          <h3>Comments ({comments.length})</h3>
          
          {/* Add Comment Form */}
          <form onSubmit={handleAddComment} style={{ marginTop: '1rem' }}>
            <div className="form-group">
              <textarea
                className="form-control"
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Add a comment..."
                rows="3"
                disabled={submittingComment}
              />
            </div>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={submittingComment || !newComment.trim()}
            >
              {submittingComment ? 'Adding...' : 'Add Comment'}
            </button>
          </form>

          {/* Comments List */}
          <div style={{ marginTop: '1.5rem' }}>
            {comments.length === 0 ? (
              <p style={{ color: '#6b7280', textAlign: 'center' }}>
                No comments yet. Be the first to comment!
              </p>
            ) : (
              comments.map((comment) => (
                <div 
                  key={comment.id}
                  style={{
                    borderTop: '1px solid #e5e7eb',
                    paddingTop: '1rem',
                    marginTop: '1rem'
                  }}
                >
                  <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between',
                    marginBottom: '0.5rem'
                  }}>
                    <strong>{comment.author.name}</strong>
                    <span style={{ color: '#6b7280', fontSize: '0.85rem' }}>
                      {new Date(comment.created_at).toLocaleString()}
                    </span>
                  </div>
                  <div style={{ whiteSpace: 'pre-wrap' }}>
                    {comment.body}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default IssueDetail;