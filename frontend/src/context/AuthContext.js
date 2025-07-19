import React, { createContext, useContext, useState, useEffect } from "react";
import { AuthAPI } from "../services/mockData";

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(null);

  useEffect(() => {
    // Check if user is logged in from localStorage
    const savedUser = localStorage.getItem("doubtSolverUser");
    const savedToken = localStorage.getItem("doubtSolverToken");
    
    if (savedUser && savedToken) {
      try {
        setUser(JSON.parse(savedUser));
        setToken(savedToken);
      } catch (error) {
        // Clear invalid data
        localStorage.removeItem("doubtSolverUser");
        localStorage.removeItem("doubtSolverToken");
      }
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await AuthAPI.login(email, password);
      
      if (response.success) {
        setUser(response.user);
        setToken(response.access_token);
        localStorage.setItem("doubtSolverUser", JSON.stringify(response.user));
        localStorage.setItem("doubtSolverToken", response.access_token);
        return { success: true };
      }
      
      return { success: false, error: response.message || "Login failed" };
    } catch (error) {
      return { success: false, error: error.message || "Login failed" };
    }
  };

  const register = async (name, email, password) => {
    try {
      const response = await AuthAPI.register(name, email, password);
      
      if (response.success) {
        setUser(response.user);
        setToken(response.access_token);
        localStorage.setItem("doubtSolverUser", JSON.stringify(response.user));
        localStorage.setItem("doubtSolverToken", response.access_token);
        return { success: true };
      }
      
      return { success: false, error: response.message || "Registration failed" };
    } catch (error) {
      return { success: false, error: error.message || "Registration failed" };
    }
  };

  const logout = async () => {
    try {
      if (token) {
        await AuthAPI.logout(token);
      }
    } catch (error) {
      // Ignore logout API errors
      console.error("Logout API error:", error);
    } finally {
      // Always clear local data
      setUser(null);
      setToken(null);
      localStorage.removeItem("doubtSolverUser");
      localStorage.removeItem("doubtSolverToken");
    }
  };

  const value = {
    user,
    token,
    login,
    register,
    logout,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};