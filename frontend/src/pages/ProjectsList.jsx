/**
 * Projects list page - shows all user's projects.
 */

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { projectsAPI } from "../api";
import Navbar from "../components/Navbar";
import { useToast } from '../context/ToastContext';  // ADD at top
import LoadingSpinner from '../components/LoadingSpinner';

const ProjectsList = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const { showToast } = useToast(); 

  // New project form state
  const [newProject, setNewProject] = useState({
    name: "",
    key: "",
    description: "",
  });

  const navigate = useNavigate();

  // Fetch projects on mount
  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
  try {
    setLoading(true);
    const data = await projectsAPI.getProjects();
    setProjects(data);
  } catch (err) {
    const errorMsg = 'Failed to load projects';
    setError(errorMsg);
    showToast(errorMsg, 'error');  // ADD THIS
    console.error(err);
  } finally {
    setLoading(false);
  }
};

const handleCreateProject = async (e) => {
  e.preventDefault();
  
  try {
    await projectsAPI.createProject(newProject);
    showToast(`Project "${newProject.name}" created successfully!`, 'success');  // ADD THIS
    setShowModal(false);
    setNewProject({ name: '', key: '', description: '' });
    fetchProjects();
  } catch (err) {
    const errorMsg = err.response?.data?.detail || 'Failed to create project';
    showToast(errorMsg, 'error');  // ADD THIS
  }
};
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

  return (
    <>
      <Navbar />
      <div className="container">
        <div className="flex justify-between items-center mb-3">
          <h2>Your Projects</h2>
          <button
            onClick={() => setShowModal(true)}
            className="btn btn-primary"
          >
            + Create Project
          </button>
        </div>

        {error && <div className="error">{error}</div>}

        {projects.length === 0 ? (
          <div className="card text-center">
            <p>No projects yet. Create your first project to get started!</p>
          </div>
        ) : (
          <div className="project-grid">
            {projects.map((project) => (
              <div key={project.id} className="card">
                <h3>{project.name}</h3>
                <p style={{ color: "#6b7280", fontSize: "0.9rem" }}>
                  Key: {project.key}
                </p>
                <p style={{ marginTop: "0.5rem" }}>
                  {project.description || "No description"}
                </p>

                {/* Add buttons */}
                <div className="flex gap-2 mt-2">
                  <button
                    onClick={() => navigate(`/projects/${project.id}/issues`)}
                    className="btn btn-primary"
                  >
                    View Issues
                  </button>
                  <button
                    onClick={() => navigate(`/projects/${project.id}`)}
                    className="btn btn-secondary"
                  >
                    Manage Team
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Create Project Modal */}
        {showModal && (
          <div className="modal-overlay" onClick={() => setShowModal(false)}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
              <h3>Create New Project</h3>

              <form onSubmit={handleCreateProject}>
                <div className="form-group">
                  <label>Project Name *</label>
                  <input
                    type="text"
                    className="form-control"
                    value={newProject.name}
                    onChange={(e) =>
                      setNewProject({ ...newProject, name: e.target.value })
                    }
                    required
                    placeholder="Backend API"
                  />
                </div>

                <div className="form-group">
                  <label>Project Key * (2-10 characters)</label>
                  <input
                    type="text"
                    className="form-control"
                    value={newProject.key}
                    onChange={(e) =>
                      setNewProject({
                        ...newProject,
                        key: e.target.value.toUpperCase(),
                      })
                    }
                    required
                    minLength="2"
                    maxLength="10"
                    placeholder="API"
                  />
                  <small style={{ color: "#6b7280" }}>
                    Used for issue IDs (e.g., API-1, API-2)
                  </small>
                </div>

                <div className="form-group">
                  <label>Description</label>
                  <textarea
                    className="form-control"
                    value={newProject.description}
                    onChange={(e) =>
                      setNewProject({
                        ...newProject,
                        description: e.target.value,
                      })
                    }
                    placeholder="What is this project about?"
                  />
                </div>

                <div className="flex gap-2">
                  <button type="submit" className="btn btn-primary">
                    Create
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

export default ProjectsList;
