import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { motion } from "framer-motion";
import { AuthProvider } from "./context/AuthContext";
import { DoubtsProvider } from "./context/DoubtsContext";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import LandingPage from "./pages/LandingPage";
import AskDoubePage from "./pages/AskDoubePage";
import HistoryPage from "./pages/HistoryPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import TutorChatPage from "./pages/TutorChatPage";
import { Toaster } from "./components/ui/toaster";

function App() {
  return (
    <AuthProvider>
      <DoubtsProvider>
        <div className="App min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
          <BrowserRouter>
            <Navbar />
            <motion.main
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="min-h-screen"
            >
              <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/ask" element={<AskDoubePage />} />
                <Route path="/history" element={<HistoryPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/tutor-chat" element={<TutorChatPage />} />
              </Routes>
            </motion.main>
            <Footer />
            <Toaster />
          </BrowserRouter>
        </div>
      </DoubtsProvider>
    </AuthProvider>
  );
}

export default App;