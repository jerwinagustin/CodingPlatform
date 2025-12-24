import api from "./api";

// Professor Authentication
export const professorRegister = async (data) => {
  const response = await api.post("/professors/register/", data);
  return response.data;
};

export const professorLogin = async (credentials) => {
  const response = await api.post("/professors/login/", credentials);
  return response.data;
};

export const getProfessorProfile = async () => {
  const response = await api.get("/professors/profile/");
  return response.data;
};

// Student Authentication
export const studentRegister = async (data) => {
  const response = await api.post("/students/register/", data);
  return response.data;
};

export const studentLogin = async (credentials) => {
  const response = await api.post("/students/login/", credentials);
  return response.data;
};

export const getStudentProfile = async () => {
  const response = await api.get("/students/profile/");
  return response.data;
};

// Token Management
export const saveTokens = (tokens, userType) => {
  localStorage.setItem("accessToken", tokens.access);
  localStorage.setItem("refreshToken", tokens.refresh);
  localStorage.setItem("userType", userType);
};

export const clearTokens = () => {
  localStorage.removeItem("accessToken");
  localStorage.removeItem("refreshToken");
  localStorage.removeItem("userType");
  localStorage.removeItem("userData");
};

export const getStoredTokens = () => {
  return {
    access: localStorage.getItem("accessToken"),
    refresh: localStorage.getItem("refreshToken"),
    userType: localStorage.getItem("userType"),
  };
};

export const isAuthenticated = () => {
  const token = localStorage.getItem("accessToken");
  return !!token;
};
