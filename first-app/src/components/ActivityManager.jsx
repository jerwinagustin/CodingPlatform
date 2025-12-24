import { useState, useEffect } from 'react';
import { activityAPI } from '../services/api';
import './ActivityManager.css';

const ActivityManager = ({ professorId }) => {
  const [activities, setActivities] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editingActivity, setEditingActivity] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    problem_statement: '',
    starter_code: '',
    expected_output: '',
    test_cases: [{ expected_output: '' }],
    difficulty: 'medium',
    time_limit: 60,
    programming_language: 'python',
    is_active: true,
    due_date: ''
  });

  useEffect(() => {
    fetchActivities();
  }, [professorId]);

  const fetchActivities = async () => {
    try {
      setLoading(true);
      const response = await activityAPI.getActivities(professorId);
      setActivities(response.data.activities || []);
      setError('');
    } catch (err) {
      setError('Failed to load activities');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleTestCaseChange = (index, field, value) => {
    const newTestCases = [...formData.test_cases];
    newTestCases[index][field] = value;
    setFormData(prev => ({ ...prev, test_cases: newTestCases }));
  };

  const addTestCase = () => {
    setFormData(prev => ({
      ...prev,
      test_cases: [...prev.test_cases, { expected_output: '' }]
    }));
  };

  const removeTestCase = (index) => {
    if (formData.test_cases.length > 1) {
      const newTestCases = formData.test_cases.filter((_, i) => i !== index);
      setFormData(prev => ({ ...prev, test_cases: newTestCases }));
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      problem_statement: '',
      starter_code: '',
      expected_output: '',
      test_cases: [{ expected_output: '' }],
      difficulty: 'medium',
      time_limit: 60,
      programming_language: 'python',
      is_active: true,
      due_date: ''
    });
    setEditingActivity(null);
    setShowForm(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      if (editingActivity) {
        await activityAPI.updateActivity(editingActivity.id, professorId, formData);
        setSuccess('Activity updated successfully!');
      } else {
        await activityAPI.createActivity(professorId, formData);
        setSuccess('Activity created successfully!');
      }
      
      await fetchActivities();
      resetForm();
      
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to save activity');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (activity) => {
    setEditingActivity(activity);
    setFormData({
      title: activity.title,
      description: activity.description,
      problem_statement: activity.problem_statement,
      starter_code: activity.starter_code || '',
      expected_output: activity.expected_output,
      test_cases: activity.test_cases.length > 0 ? activity.test_cases : [{ expected_output: '' }],
      difficulty: activity.difficulty,
      time_limit: activity.time_limit,
      programming_language: activity.programming_language,
      is_active: activity.is_active,
      due_date: activity.due_date ? activity.due_date.split('T')[0] : ''
    });
    setShowForm(true);
  };

  const handleDelete = async (activityId) => {
    if (!window.confirm('Are you sure you want to delete this activity?')) {
      return;
    }

    try {
      setLoading(true);
      await activityAPI.deleteActivity(activityId, professorId);
      setSuccess('Activity deleted successfully!');
      await fetchActivities();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to delete activity');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="activity-manager">
      <div className="activity-header">
        <h2>Activity Management</h2>
        <button 
          className="btn-primary"
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? 'Cancel' : '+ Create New Activity'}
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {showForm && (
        <div className="activity-form-container">
          <h3>{editingActivity ? 'Edit Activity' : 'Create New Activity'}</h3>
          <form onSubmit={handleSubmit} className="activity-form">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="title">Title *</label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  required
                  placeholder="e.g., Two Sum Problem"
                />
              </div>

              <div className="form-group">
                <label htmlFor="difficulty">Difficulty</label>
                <select
                  id="difficulty"
                  name="difficulty"
                  value={formData.difficulty}
                  onChange={handleInputChange}
                >
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="description">Description *</label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                required
                rows="3"
                placeholder="Brief description of the activity"
              />
            </div>

            <div className="form-group">
              <label htmlFor="problem_statement">Problem Statement *</label>
              <textarea
                id="problem_statement"
                name="problem_statement"
                value={formData.problem_statement}
                onChange={handleInputChange}
                required
                rows="5"
                placeholder="Detailed problem description..."
              />
            </div>

            <div className="form-group">
              <label htmlFor="starter_code">Starter Code (Optional)</label>
              <textarea
                id="starter_code"
                name="starter_code"
                value={formData.starter_code}
                onChange={handleInputChange}
                rows="4"
                placeholder="def solve(input):&#10;    # Your code here&#10;    pass"
                style={{ fontFamily: 'monospace' }}
              />
            </div>

            <div className="form-group">
              <label htmlFor="expected_output">Expected Output *</label>
              <textarea
                id="expected_output"
                name="expected_output"
                value={formData.expected_output}
                onChange={handleInputChange}
                required
                rows="3"
                placeholder="Expected output format or example"
              />
            </div>

            <div className="form-group">
              <label>Expected Outputs (Test Cases) *</label>
              {formData.test_cases.map((testCase, index) => (
                <div key={index} className="test-case-row">
                  <input
                    type="text"
                    value={testCase.expected_output}
                    onChange={(e) => handleTestCaseChange(index, 'expected_output', e.target.value)}
                    placeholder={`Expected Output ${index + 1}`}
                    required
                  />
                  <button
                    type="button"
                    onClick={() => removeTestCase(index)}
                    className="btn-remove"
                    disabled={formData.test_cases.length === 1}
                  >
                    ✕
                  </button>
                </div>
              ))}
              <button type="button" onClick={addTestCase} className="btn-secondary">
                + Add Expected Output
              </button>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="programming_language">Programming Language</label>
                <select
                  id="programming_language"
                  name="programming_language"
                  value={formData.programming_language}
                  onChange={handleInputChange}
                >
                  <option value="python">Python</option>
                  <option value="javascript">JavaScript</option>
                  <option value="java">Java</option>
                  <option value="cpp">C++</option>
                  <option value="c">C</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="time_limit">Time Limit (minutes)</label>
                <input
                  type="number"
                  id="time_limit"
                  name="time_limit"
                  value={formData.time_limit}
                  onChange={handleInputChange}
                  min="1"
                  max="300"
                />
              </div>

              <div className="form-group">
                <label htmlFor="due_date">Due Date</label>
                <input
                  type="date"
                  id="due_date"
                  name="due_date"
                  value={formData.due_date}
                  onChange={handleInputChange}
                />
              </div>
            </div>

            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  name="is_active"
                  checked={formData.is_active}
                  onChange={handleInputChange}
                />
                Active (visible to students)
              </label>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn-primary" disabled={loading}>
                {loading ? 'Saving...' : editingActivity ? 'Update Activity' : 'Create Activity'}
              </button>
              <button type="button" onClick={resetForm} className="btn-secondary">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="activities-list">
        <h3>Your Activities ({activities.length})</h3>
        {loading && <p>Loading activities...</p>}
        
        {!loading && activities.length === 0 && (
          <p className="no-activities">No activities created yet. Click "Create New Activity" to get started!</p>
        )}

        {!loading && activities.length > 0 && (
          <div className="activities-grid">
            {activities.map(activity => (
              <div key={activity.id} className="activity-card">
                <div className="activity-card-header">
                  <h4>{activity.title}</h4>
                  <span className={`badge badge-${activity.difficulty}`}>
                    {activity.difficulty}
                  </span>
                </div>
                
                <p className="activity-description">{activity.description}</p>
                
                <div className="activity-meta">
                  <span>⏱️ {activity.time_limit} min</span>
                  <span>💻 {activity.programming_language}</span>
                  <span className={activity.is_active ? 'status-active' : 'status-inactive'}>
                    {activity.is_active ? '✓ Active' : '✕ Inactive'}
                  </span>
                </div>

                {activity.due_date && (
                  <div className="activity-due-date">
                    📅 Due: {new Date(activity.due_date).toLocaleDateString()}
                  </div>
                )}

                <div className="activity-actions">
                  <button 
                    onClick={() => handleEdit(activity)}
                    className="btn-edit"
                  >
                    Edit
                  </button>
                  <button 
                    onClick={() => handleDelete(activity.id)}
                    className="btn-delete"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ActivityManager;
