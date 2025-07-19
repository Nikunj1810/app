import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8001";
const API = `${BACKEND_URL}/api`;

// Mock data for development/fallback
export const mockDoubts = [
  {
    id: "1",
    question: "What is the derivative of x²?",
    subject: "mathematics", 
    question_type: "text",
    answer: {
      solution: "The derivative of x² is 2x",
      steps: ["Apply the power rule", "Bring down the exponent", "Subtract 1 from the exponent"],
      generated_at: "2024-01-15T10:30:00Z"
    },
    status: "answered",
    created_at: "2024-01-15T10:25:00Z",
    updated_at: "2024-01-15T10:30:00Z"
  }
];

export const subjects = [
  "mathematics",
  "physics", 
  "chemistry",
  "biology",
  "english",
  "history",
  "geography",
  "computer science"
];

export const mockAIResponse = async (question, subject) => {
  // Simulate AI processing delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  return {
    id: Math.random().toString(36).substr(2, 9),
    question,
    subject,
    question_type: "text",
    answer: {
      solution: `Here's a step-by-step solution for your ${subject} question: "${question}"`,
      steps: [
        "Understand the problem",
        "Identify key concepts", 
        "Apply relevant formulas",
        "Calculate the result",
        "Verify the answer"
      ],
      generated_at: new Date().toISOString()
    },
    status: "answered",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };
};

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
  static async createTextQuestion(question, subject, token) {
    try {
      const data = { question, subject };

      const config = {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      };

      const response = await axios.post(`${API}/questions/text`, data, config);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || "Failed to create text question");
    }
  }

  static async createImageQuestion(file, question, subject, token) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('question', question || '');
      formData.append('subject', subject);

      const config = {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      };

      const response = await axios.post(`${API}/questions/image`, formData, config);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || "Failed to create image question");
    }
  }

  static async getUserQuestions(userId, token, skip = 0, limit = 50) {
    try {
      const response = await axios.get(`${API}/questions/user/${userId}?skip=${skip}&limit=${limit}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || "Failed to get questions");
    }
  }

  // Legacy methods for backward compatibility
  static async createDoubt(question, subject, questionType = "text", imageData = null, token = null) {
    if (questionType === "text") {
      return this.createTextQuestion(question, subject, token);
    } else {
      // For image type, we'll need to convert base64 back to file
      throw new Error("Use createImageQuestion for image uploads");
    }
  }

  static async getUserDoubts(token, skip = 0, limit = 50) {
    try {
      // Get current user first to get user ID
      const userResponse = await axios.get(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const userId = userResponse.data.id;
      
      return this.getUserQuestions(userId, token, skip, limit);
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

// Chat API service
export class ChatAPI {
  static async sendMessage(message, doubtId = null, token) {
    try {
      const data = { message, doubt_id: doubtId };
      
      const response = await axios.post(`${API}/chat/send`, data, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || "Failed to send message");
    }
  }

  static async getMessages(doubtId = null, token, limit = 50) {
    try {
      const params = { limit };
      if (doubtId) params.doubt_id = doubtId;
      
      const response = await axios.get(`${API}/chat/messages`, {
        headers: {
          Authorization: `Bearer ${token}`
        },
        params
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || "Failed to get messages");
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