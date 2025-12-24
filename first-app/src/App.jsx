import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

// Pages
import Home from './pages/Home';
import ProfessorLogin from './pages/ProfessorLogin';
import ProfessorRegister from './pages/ProfessorRegister';
import ProfessorDashboard from './pages/ProfessorDashboard';
import StudentLogin from './pages/StudentLogin';
import StudentRegister from './pages/StudentRegister';
import StudentDashboard from './pages/StudentDashboard';
import FeedbackPage from './pages/FeedbackPage';

import './App.css';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Home />} />
          
          {/* Professor Routes */}
          <Route path="/professor/login" element={<ProfessorLogin />} />
          <Route path="/professor/register" element={<ProfessorRegister />} />
          <Route 
            path="/professor/dashboard" 
            element={
              <ProtectedRoute userType="professor">
                <ProfessorDashboard />
              </ProtectedRoute>
            } 
          />
          
          {/* Student Routes */}
          <Route path="/student/login" element={<StudentLogin />} />
          <Route path="/student/register" element={<StudentRegister />} />
          <Route 
            path="/student/dashboard" 
            element={
              <ProtectedRoute userType="student">
                <StudentDashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/student/feedback/:submissionId" 
            element={
              <ProtectedRoute userType="student">
                <FeedbackPage />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
