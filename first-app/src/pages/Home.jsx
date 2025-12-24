import { Link } from 'react-router-dom';
import './Home.css';

const Home = () => {
  return (
    <div className="home-container">
      <div className="home-content">
        <h1 className="home-title">University Management System</h1>
        <p className="home-subtitle">Choose your role to continue</p>
        
        <div className="role-cards">
          <div className="role-card">
            <div className="role-icon">👨‍🏫</div>
            <h2>Professor</h2>
            <p>Access your courses and manage student records</p>
            <div className="role-actions">
              <Link to="/professor/login" className="btn btn-login">
                Login
              </Link>
              <Link to="/professor/register" className="btn btn-register">
                Register
              </Link>
            </div>
          </div>

          <div className="role-card">
            <div className="role-icon">👨‍🎓</div>
            <h2>Student</h2>
            <p>View your courses and track your progress</p>
            <div className="role-actions">
              <Link to="/student/login" className="btn btn-login">
                Login
              </Link>
              <Link to="/student/register" className="btn btn-register">
                Register
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
