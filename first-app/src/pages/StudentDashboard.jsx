import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import api from '../services/api';
import ActivityModule from '../components/ActivityModule';
import './Dashboard.css';

const StudentDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [viewMode, setViewMode] = useState('list'); // 'list' or 'activity'

  useEffect(() => {
    fetchActivities();
  }, []);

  const fetchActivities = async () => {
    try {
      setLoading(true);
      const response = await api.get('/students/activities/');
      setActivities(response.data.activities || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching activities:', err);
      setError('Failed to load activities');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'No deadline';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy': return '#4caf50';
      case 'medium': return '#ff9800';
      case 'hard': return '#f44336';
      default: return '#757575';
    }
  };

  const handleStartActivity = (activity) => {
    setSelectedActivity(activity);
    setViewMode('activity');
  };

  const handleBackToList = () => {
    setSelectedActivity(null);
    setViewMode('list');
  };

  const handleSubmitSuccess = (result) => {
    console.log('Submission successful:', result);
    // You could show a toast notification here
  };

  // If viewing an activity, show the ActivityModule
  if (viewMode === 'activity' && selectedActivity) {
    return (
      <ActivityModule
        activity={selectedActivity}
        studentId={user?.id}
        onBack={handleBackToList}
        onSubmitSuccess={handleSubmitSuccess}
      />
    );
  }

  return (
    <div className="dashboard-container">
      <nav className="dashboard-nav">
        <h2>Student Portal</h2>
        <button onClick={handleLogout} className="btn-logout">
          Logout
        </button>
      </nav>

      <div className="dashboard-content">
        <div className="welcome-card">
          <h1>Welcome, {user?.first_name} {user?.last_name}!</h1>
          <p className="subtitle">Student ID: {user?.student_id}</p>
        </div>

        <div className="info-grid">
          <div className="info-card">
            <h3>Profile Information</h3>
            <div className="info-item">
              <span className="label">Email:</span>
              <span className="value">{user?.email}</span>
            </div>
            <div className="info-item">
              <span className="label">Program:</span>
              <span className="value">{user?.program}</span>
            </div>
            <div className="info-item">
              <span className="label">Year:</span>
              <span className="value">{user?.year}</span>
            </div>
            <div className="info-item">
              <span className="label">Phone:</span>
              <span className="value">{user?.phone || 'Not provided'}</span>
            </div>
            <div className="info-item">
              <span className="label">Status:</span>
              <span className="value status-active">Active</span>
            </div>
          </div>

          <div className="info-card">
            <h3>Quick Actions</h3>
            <div className="action-buttons">
              <button className="action-btn">View Courses</button>
              <button className="action-btn">Assignments</button>
              <button className="action-btn">Grades</button>
              <button className="action-btn">Settings</button>
            </div>
          </div>
        </div>

        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📚</div>
            <div className="stat-value">6</div>
            <div className="stat-label">Enrolled Courses</div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">📝</div>
            <div className="stat-value">{activities.length}</div>
            <div className="stat-label">Pending Activities</div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">⭐</div>
            <div className="stat-value">3.8</div>
            <div className="stat-label">GPA</div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">🎓</div>
            <div className="stat-value">85%</div>
            <div className="stat-label">Attendance</div>
          </div>
        </div>

        {/* Activities Section */}
        <div className="activities-section">
          <h2>Pending Activities</h2>
          
          {loading && (
            <div className="loading-message">Loading activities...</div>
          )}
          
          {error && (
            <div className="error-message">{error}</div>
          )}
          
          {!loading && !error && activities.length === 0 && (
            <div className="no-activities">
              <p>🎉 No pending activities at the moment!</p>
            </div>
          )}
          
          {!loading && !error && activities.length > 0 && (
            <div className="activities-grid">
              {activities.map((activity) => (
                <div key={activity.id} className="activity-card">
                  <div className="activity-header">
                    <h3>{activity.title}</h3>
                    <span 
                      className="difficulty-badge"
                      style={{ backgroundColor: getDifficultyColor(activity.difficulty) }}
                    >
                      {activity.difficulty}
                    </span>
                  </div>
                  
                  <p className="activity-description">{activity.description}</p>
                  
                  <div className="activity-details">
                    <div className="detail-item">
                      <span className="detail-label">Professor:</span>
                      <span className="detail-value">{activity.professor_name}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Language:</span>
                      <span className="detail-value">{activity.programming_language}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Time Limit:</span>
                      <span className="detail-value">{activity.time_limit} min</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Due Date:</span>
                      <span className="detail-value">{formatDate(activity.due_date)}</span>
                    </div>
                  </div>
                  
                  <div className="activity-problem">
                    <strong>Problem Statement:</strong>
                    <p>{activity.problem_statement}</p>
                  </div>
                  
                  <button 
                    className="btn-view-activity"
                    onClick={() => handleStartActivity(activity)}
                  >
                    Start Activity
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;
