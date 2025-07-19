import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { useDoubts } from "../context/DoubtsContext";
import { useAuth } from "../context/AuthContext";
import { 
  History, 
  BookOpen, 
  Calendar, 
  Trash2, 
  Eye, 
  Image as ImageIcon,
  FileText,
  Clock,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  Sparkles
} from "lucide-react";

const HistoryPage = () => {
  const { doubts, deleteDoubt } = useDoubts();
  const { user } = useAuth();
  const [expandedCards, setExpandedCards] = useState({});
  const [filter, setFilter] = useState("all");

  const toggleCard = (doubtId) => {
    setExpandedCards(prev => ({
      ...prev,
      [doubtId]: !prev[doubtId]
    }));
  };

  const handleDelete = (doubtId) => {
    if (window.confirm("Are you sure you want to delete this doubt?")) {
      deleteDoubt(doubtId);
    }
  };

  const filteredDoubts = doubts.filter(doubt => {
    if (filter === "all") return true;
    if (filter === "text") return doubt.type === "text";
    if (filter === "image") return doubt.type === "image";
    return true;
  });

  const getSubjectColor = (subject) => {
    const colors = {
      "Mathematics": "bg-blue-100 text-blue-800",
      "Physics": "bg-purple-100 text-purple-800", 
      "Chemistry": "bg-green-100 text-green-800",
      "Biology": "bg-yellow-100 text-yellow-800",
      "English": "bg-pink-100 text-pink-800",
      "History": "bg-orange-100 text-orange-800",
      "Computer Science": "bg-indigo-100 text-indigo-800",
      "default": "bg-gray-100 text-gray-800"
    };
    return colors[subject] || colors.default;
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-20">
            <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Login Required</h2>
            <p className="text-gray-600 mb-6">Please login to view your doubt history</p>
            <Button asChild>
              <a href="/login">Go to Login</a>
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Your{" "}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              History
            </span>
          </h1>
          <p className="text-lg text-gray-600">
            Review your past questions and AI-generated solutions
          </p>
        </motion.div>

        {/* Filter Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="flex flex-wrap justify-center gap-4 mb-8"
        >
          <Button
            variant={filter === "all" ? "default" : "outline"}
            onClick={() => setFilter("all")}
            className="flex items-center space-x-2"
          >
            <BookOpen className="w-4 h-4" />
            <span>All ({doubts.length})</span>
          </Button>
          <Button
            variant={filter === "text" ? "default" : "outline"}
            onClick={() => setFilter("text")}
            className="flex items-center space-x-2"
          >
            <FileText className="w-4 h-4" />
            <span>Text ({doubts.filter(d => d.type === "text").length})</span>
          </Button>
          <Button
            variant={filter === "image" ? "default" : "outline"}
            onClick={() => setFilter("image")}
            className="flex items-center space-x-2"
          >
            <ImageIcon className="w-4 h-4" />
            <span>Image ({doubts.filter(d => d.type === "image").length})</span>
          </Button>
        </motion.div>

        {/* Doubts List */}
        <div className="space-y-6">
          <AnimatePresence>
            {filteredDoubts.length === 0 ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-center py-20"
              >
                <History className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-700 mb-2">No doubts found</h3>
                <p className="text-gray-500 mb-6">
                  {filter === "all" 
                    ? "You haven't asked any questions yet. Start by asking your first doubt!"
                    : `No ${filter} questions found. Try a different filter.`
                  }
                </p>
                <Button asChild>
                  <a href="/ask">Ask Your First Doubt</a>
                </Button>
              </motion.div>
            ) : (
              filteredDoubts.map((doubt, index) => (
                <motion.div
                  key={doubt.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  layout
                >
                  <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm hover:shadow-xl transition-shadow">
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-3">
                            <Badge className={getSubjectColor(doubt.subject)}>
                              {doubt.subject}
                            </Badge>
                            <Badge variant="outline" className="flex items-center space-x-1">
                              {doubt.type === "image" ? (
                                <ImageIcon className="w-3 h-3" />
                              ) : (
                                <FileText className="w-3 h-3" />
                              )}
                              <span>{doubt.type}</span>
                            </Badge>
                            <div className="flex items-center text-sm text-gray-500">
                              <Clock className="w-4 h-4 mr-1" />
                              {formatDate(doubt.timestamp)}
                            </div>
                          </div>
                          
                          <CardTitle className="text-lg leading-relaxed mb-2">
                            {doubt.question}
                          </CardTitle>

                          {doubt.image && (
                            <div className="mt-3">
                              <img
                                src={doubt.image}
                                alt="Question image"
                                className="max-w-sm rounded-lg border shadow-sm"
                              />
                            </div>
                          )}
                        </div>

                        <div className="flex items-center space-x-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => toggleCard(doubt.id)}
                            className="flex items-center space-x-1"
                          >
                            {expandedCards[doubt.id] ? (
                              <>
                                <ChevronUp className="w-4 h-4" />
                                <span>Hide</span>
                              </>
                            ) : (
                              <>
                                <Eye className="w-4 h-4" />
                                <span>View</span>
                              </>
                            )}
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(doubt.id)}
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </CardHeader>

                    <AnimatePresence>
                      {expandedCards[doubt.id] && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={{ duration: 0.3 }}
                        >
                          <CardContent className="pt-0">
                            <div className="border-t pt-4">
                              <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-4 border border-green-200 mb-4">
                                <h4 className="font-semibold text-green-800 mb-2 flex items-center">
                                  <Sparkles className="w-4 h-4 mr-2" />
                                  AI Solution
                                </h4>
                                <div className="text-gray-800 whitespace-pre-line">
                                  {doubt.answer.solution}
                                </div>
                              </div>

                              {doubt.answer.steps && (
                                <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                                  <h4 className="font-semibold text-blue-800 mb-3">Steps:</h4>
                                  <ol className="list-decimal list-inside space-y-2">
                                    {doubt.answer.steps.map((step, stepIndex) => (
                                      <li key={stepIndex} className="text-gray-700">
                                        {step}
                                      </li>
                                    ))}
                                  </ol>
                                </div>
                              )}
                            </div>
                          </CardContent>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </Card>
                </motion.div>
              ))
            )}
          </AnimatePresence>
        </div>

        {/* Stats */}
        {filteredDoubts.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="mt-12 text-center"
          >
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="bg-white/50 border-0">
                <CardContent className="pt-6">
                  <div className="text-3xl font-bold text-blue-600 mb-2">
                    {doubts.length}
                  </div>
                  <div className="text-sm text-gray-600">Total Questions</div>
                </CardContent>
              </Card>
              
              <Card className="bg-white/50 border-0">
                <CardContent className="pt-6">
                  <div className="text-3xl font-bold text-green-600 mb-2">
                    {doubts.filter(d => d.status === "answered").length}
                  </div>
                  <div className="text-sm text-gray-600">Answered</div>
                </CardContent>
              </Card>
              
              <Card className="bg-white/50 border-0">
                <CardContent className="pt-6">
                  <div className="text-3xl font-bold text-purple-600 mb-2">
                    {new Set(doubts.map(d => d.subject)).size}
                  </div>
                  <div className="text-sm text-gray-600">Subjects</div>
                </CardContent>
              </Card>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default HistoryPage;