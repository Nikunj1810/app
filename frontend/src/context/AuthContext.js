import React, { createContext, useContext, useState, useEffect } from "react";

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

  useEffect(() => {
    // Check if user is logged in from localStorage
    const savedUser = localStorage.getItem("doubtSolverUser");
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    // Mock login - in real app, this would call backend API
    if (email && password) {
      const mockUser = {
        id: "user_123",
        email: email,
        name: email.split("@")[0],
        joinDate: new Date().toISOString(),
      };
      setUser(mockUser);
      localStorage.setItem("doubtSolverUser", JSON.stringify(mockUser));
      return { success: true };
    }
    return { success: false, error: "Invalid credentials" };
  };

  const register = async (name, email, password) => {
    // Mock register - in real app, this would call backend API
    if (name && email && password) {
      const mockUser = {
        id: "user_" + Math.random().toString(36).substr(2, 9),
        email: email,
        name: name,
        joinDate: new Date().toISOString(),
      };
      setUser(mockUser);
      localStorage.setItem("doubtSolverUser", JSON.stringify(mockUser));
      return { success: true };
    }
    return { success: false, error: "All fields are required" };
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("doubtSolverUser");
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};