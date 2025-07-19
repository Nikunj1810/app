import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8001";
const API = `${BACKEND_URL}/api`;

// API service for authentication
export class AuthAPI {
  static async register(name, email, password) {
    try {
      const response = await axios.post(`${API}/auth/register`, {
        name,
        email,
        password
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || "Registration failed");
    }
  }

  static async login(email, password) {
    try {
      const response = await axios.post(`${API}/auth/login`, {
        email,
        password
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || "Login failed");
    }
  }

  static async getCurrentUser(token) {
    try {
      const response = await axios.get(`${API}/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || "Failed to get user info");
    }
  }

  static async logout(token) {
    try {
      const response = await axios.post(`${API}/auth/logout`, {}, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || "Logout failed");
    }
  }
}

// API service for doubts
export class DoubtsAPI {
  static async createDoubt(question, subject, questionType = "text", imageData = null, token = null) {
    try {
      const data = {
        question,
        subject,
        question_type: questionType,
        ...(imageData && { image_data: imageData })
      };

      const config = token ? {
        headers: {
          Authorization: `Bearer ${token}`
        }
      } : {};

      // Use demo endpoint if no token (for guest users)
      const endpoint = token ? `${API}/doubts/` : `${API}/doubts/demo`;
      
      const response = await axios.post(endpoint, data, config);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || "Failed to create doubt");
    }
  }

  static async getUserDoubts(token, skip = 0, limit = 50) {
    try {
      const response = await axios.get(`${API}/doubts/?skip=${skip}&limit=${limit}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || "Failed to get doubts");
    }
  }

  static async getDoubt(doubtId, token) {
    try {
      const response = await axios.get(`${API}/doubts/${doubtId}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || "Failed to get doubt");
    }
  }

  static async deleteDoubt(doubtId, token) {
    try {
      const response = await axios.delete(`${API}/doubts/${doubtId}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || "Failed to delete doubt");
    }
  }
}

// Health check
export const checkBackendHealth = async () => {
  try {
    const response = await axios.get(`${API}/`);
    return response.data;
  } catch (error) {
    throw new Error("Backend is not responding");
  }
};