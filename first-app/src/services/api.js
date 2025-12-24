import axios from "axios";

const API_BASE_URL = "http://localhost:8000/api";

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("accessToken");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Only handle 401 for endpoints that specifically require auth
    // Don't auto-logout for activity endpoints
    const isAuthRequired =
      !originalRequest.url.includes("/activities/") &&
      !originalRequest.url.includes("/register/") &&
      !originalRequest.url.includes("/login/");

    // If token expired and this is an auth-required endpoint, try to refresh
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      isAuthRequired
    ) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem("refreshToken");
      if (refreshToken) {
        try {
          // Note: You might need to implement a refresh endpoint
          // For now, just redirect to login
          localStorage.removeItem("accessToken");
          localStorage.removeItem("refreshToken");
          localStorage.removeItem("userType");
          localStorage.removeItem("user");
          window.location.href = "/";
        } catch (refreshError) {
          return Promise.reject(refreshError);
        }
      }
    }

    return Promise.reject(error);
  }
);

// Activity API endpoints
export const activityAPI = {
  // Create a new activity
  createActivity: (professorId, activityData) => {
    return api.post("/professors/activities/create/", {
      ...activityData,
      professor_id: professorId,
    });
  },

  // Get all activities for a professor
  getActivities: (professorId) => {
    return api.get("/professors/activities/", {
      params: { professor_id: professorId },
    });
  },

  // Get a specific activity
  getActivity: (activityId) => {
    return api.get(`/professors/activities/${activityId}/`);
  },

  // Update an activity
  updateActivity: (activityId, professorId, activityData) => {
    return api.put(`/professors/activities/${activityId}/update/`, {
      ...activityData,
      professor_id: professorId,
    });
  },

  // Delete an activity
  deleteActivity: (activityId, professorId) => {
    return api.delete(`/professors/activities/${activityId}/delete/`, {
      data: { professor_id: professorId },
    });
  },
};

// Code Execution API endpoints (for students)
export const codeAPI = {
  // Run code for quick testing (no grading)
  runCode: (activityId, code, language = "python", input = "") => {
    return api.post("/students/code/run/", {
      activity_id: activityId,
      code,
      language,
      input,
    });
  },

  // Submit code for grading (async with Celery)
  submitCode: (activityId, studentId, code, language = "python") => {
    return api.post("/students/code/submit/", {
      activity_id: activityId,
      student_id: studentId,
      code,
      language,
    });
  },

  // Submit code for grading (sync - waits for result)
  submitCodeSync: (activityId, studentId, code, language = "python") => {
    return api.post("/students/code/submit-sync/", {
      activity_id: activityId,
      student_id: studentId,
      code,
      language,
    });
  },

  // Get submission status (for async submissions)
  getSubmissionStatus: (submissionId) => {
    return api.get(`/students/submissions/${submissionId}/status/`);
  },

  // Get AI feedback for a submission
  getAIFeedback: (submissionId) => {
    return api.get(`/students/submissions/${submissionId}/ai-feedback/`);
  },

  // Get all submissions for a student
  getSubmissions: (studentId, activityId = null) => {
    const params = { student_id: studentId };
    if (activityId) params.activity_id = activityId;
    return api.get("/students/submissions/", { params });
  },

  // Get activity details for students
  getActivityDetail: (activityId) => {
    return api.get(`/students/activities/${activityId}/`);
  },
};

export default api;
