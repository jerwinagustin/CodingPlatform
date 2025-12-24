import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import ActivityManager from '../components/ActivityManager';
import './Dashboard.css';

const ProfessorDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('dashboard');

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="dashboard-container">
      <nav className="dashboard-nav">
        <h2>Professor Portal</h2>
        <div className="nav-tabs">
          <button 
            className={`nav-tab ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>
          <button 
            className={`nav-tab ${activeTab === 'activities' ? 'active' : ''}`}
            onClick={() => setActiveTab('activities')}
          >
            Activities
          </button>
        </div>
        <button onClick={handleLogout} className="btn-logout">
          Logout
        </button>
      </nav>

      <div className="dashboard-content">
        {activeTab === 'dashboard' && (
          <>
            <div className="welcome-card">
              <h1>Welcome, Prof. {user?.first_name} {user?.last_name}!</h1>
              <p className="subtitle">Employee ID: {user?.employee_id}</p>
            </div>

            <div className="info-grid">
              <div className="info-card">
                <h3>Profile Information</h3>
                <div className="info-item">
                  <span className="label">Email:</span>
                  <span className="value">{user?.email}</span>
                </div>
                <div className="info-item">
                  <span className="label">Department:</span>
                  <span className="value">{user?.department}</span>
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
                  <button 
                    className="action-btn"
                    onClick={() => setActiveTab('activities')}
                  >
                    Manage Activities
                  </button>
                  <button className="action-btn">View Courses</button>
                  <button className="action-btn">Manage Students</button>
                  <button className="action-btn">Schedule</button>
                </div>
              </div>
            </div>

            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon">📚</div>
                <div className="stat-value">5</div>
                <div className="stat-label">Courses</div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">👥</div>
                <div className="stat-value">120</div>
                <div className="stat-label">Students</div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">📝</div>
                <div className="stat-value">15</div>
                <div className="stat-label">Assignments</div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">📊</div>
                <div className="stat-value">8</div>
                <div className="stat-label">Exams</div>
              </div>
            </div>
          </>
        )}

        {activeTab === 'activities' && (
          <ActivityManager professorId={user?.id} />
        )}
      </div>
    </div>
  );
};

export default ProfessorDashboard;
