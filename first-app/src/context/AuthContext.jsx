import { createContext, useContext, useState, useEffect } from 'react';
import { 
  professorLogin, 
  professorRegister, 
  studentLogin, 
  studentRegister,
  saveTokens, 
  clearTokens, 
  isAuthenticated as checkAuth 
} from '../services/authService';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [userType, setUserType] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if user is already logged in
    const storedUserType = localStorage.getItem('userType');
    const storedUser = localStorage.getItem('userData');
    const authenticated = checkAuth();

    if (authenticated && storedUser) {
      setUser(JSON.parse(storedUser));
      setUserType(storedUserType);
      setIsAuthenticated(true);
    }
    setLoading(false);
  }, []);

  const loginProfessor = async (credentials) => {
    try {
      const response = await professorLogin(credentials);
      saveTokens(response.tokens, 'professor');
      setUser(response.professor);
      setUserType('professor');
      setIsAuthenticated(true);
      localStorage.setItem('userData', JSON.stringify(response.professor));
      return { success: true, data: response };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Login failed' 
      };
    }
  };

  const registerProfessor = async (data) => {
    try {
      const response = await professorRegister(data);
      saveTokens(response.tokens, 'professor');
      setUser(response.professor);
      setUserType('professor');
      setIsAuthenticated(true);
      localStorage.setItem('userData', JSON.stringify(response.professor));
      return { success: true, data: response };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || error.response?.data || 'Registration failed' 
      };
    }
  };

  const loginStudent = async (credentials) => {
    try {
      const response = await studentLogin(credentials);
      saveTokens(response.tokens, 'student');
      setUser(response.student);
      setUserType('student');
      setIsAuthenticated(true);
      localStorage.setItem('userData', JSON.stringify(response.student));
      return { success: true, data: response };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Login failed' 
      };
    }
  };

  const registerStudent = async (data) => {
    try {
      const response = await studentRegister(data);
      saveTokens(response.tokens, 'student');
      setUser(response.student);
      setUserType('student');
      setIsAuthenticated(true);
      localStorage.setItem('userData', JSON.stringify(response.student));
      return { success: true, data: response };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || error.response?.data || 'Registration failed' 
      };
    }
  };

  const logout = () => {
    clearTokens();
    setUser(null);
    setUserType(null);
    setIsAuthenticated(false);
  };

  const value = {
    user,
    userType,
    isAuthenticated,
    loading,
    loginProfessor,
    registerProfessor,
    loginStudent,
    registerStudent,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
