import React, { createContext, useContext, useState } from "react";
import { mockDoubts } from "../services/mockData";

const DoubtsContext = createContext();

export const useDoubts = () => {
  const context = useContext(DoubtsContext);
  if (!context) {
    throw new Error("useDoubts must be used within a DoubtsProvider");
  }
  return context;
};

export const DoubtsProvider = ({ children }) => {
  const [doubts, setDoubts] = useState(mockDoubts);
  const [loading, setLoading] = useState(false);

  const addDoubt = (newDoubt) => {
    const doubtWithId = {
      ...newDoubt,
      id: "doubt_" + Math.random().toString(36).substr(2, 9),
      timestamp: new Date().toISOString(),
      status: "answered",
    };
    setDoubts(prev => [doubtWithId, ...prev]);
    return doubtWithId;
  };

  const getDoubtById = (id) => {
    return doubts.find(doubt => doubt.id === id);
  };

  const deleteDoubt = (id) => {
    setDoubts(prev => prev.filter(doubt => doubt.id !== id));
  };

  const value = {
    doubts,
    loading,
    addDoubt,
    getDoubtById,
    deleteDoubt,
    setLoading,
  };

  return <DoubtsContext.Provider value={value}>{children}</DoubtsContext.Provider>;
};