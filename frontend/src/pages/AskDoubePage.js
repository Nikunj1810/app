import React, { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Textarea } from "../components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { useToast } from "../hooks/use-toast";
import { useDoubts } from "../context/DoubtsContext";
import { useAuth } from "../context/AuthContext";
import { DoubtsAPI, subjects } from "../services/mockData";
import { 
  Upload, 
  Camera, 
  FileImage, 
  X, 
  Send, 
  BookOpen,
  Loader2,
  Sparkles,
  AlertCircle
} from "lucide-react";

const AskDoubePage = () => {
  const [question, setQuestion] = useState("");
  const [subject, setSubject] = useState("");
  const [uploadedImage, setUploadedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState(null);
  const fileInputRef = useRef(null);
  
  const { toast } = useToast();
  const { addDoubt } = useDoubts();
  const { user } = useAuth();
  const navigate = useNavigate();

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        toast({
          title: "File too large",
          description: "Please upload an image smaller than 5MB",
          variant: "destructive"
        });
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        const base64 = e.target.result;
        setUploadedImage(base64);
        setImagePreview(base64);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeImage = () => {
    setUploadedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!question.trim() && !uploadedImage) {
      toast({
        title: "Missing input",
        description: "Please enter a question or upload an image",
        variant: "destructive"
      });
      return;
    }

    if (!subject) {
      toast({
        title: "Subject required", 
        description: "Please select a subject",
        variant: "destructive"
      });
      return;
    }

    setIsLoading(true);
    setAiResponse(null);

    try {
      // Call the enhanced backend API
      let response;
      if (uploadedImage) {
        // Convert base64 to File object for image upload
        const base64Data = uploadedImage.split(',')[1];
        const byteCharacters = atob(base64Data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const file = new File([byteArray], 'image.png', { type: 'image/png' });
        
        response = await DoubtsAPI.createImageQuestion(file, question, subject, user.token);
      } else {
        response = await DoubtsAPI.createTextQuestion(question, subject, user.token);
      }

      // Format the response to match frontend expectations
      const formattedResponse = {
        id: response.id,
        question: response.question,
        subject: response.subject,
        solution: response.answer?.solution || "Processing...",
        steps: response.answer?.steps || [],
        status: response.status,
        created_at: response.created_at
      };

      setAiResponse(formattedResponse);

      // Add to doubts history
      const newDoubt = {
        question: question || "Image-based question",
        subject,
        type: uploadedImage ? "image" : "text",
        image: uploadedImage,
        answer: response,
        userId: user?.id || "guest"
      };

      addDoubt(newDoubt);

      toast({
        title: "Answer generated!",
        description: "Your doubt has been solved successfully",
      });

    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to get answer. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setQuestion("");
    setSubject("");
    setUploadedImage(null);
    setImagePreview(null);
    setAiResponse(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Ask Your{" "}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Doubt
            </span>
          </h1>
          <p className="text-lg text-gray-600">
            Get instant AI-powered solutions with step-by-step explanations
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Question Input Section */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BookOpen className="w-5 h-5 text-blue-600" />
                  <span>Submit Your Question</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <form onSubmit={handleSubmit} className="space-y-6">
                  {/* Subject Selection */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Subject *
                    </label>
                    <Select value={subject} onValueChange={setSubject}>
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="Select a subject" />
                      </SelectTrigger>
                      <SelectContent>
                        {subjects.map((subj) => (
                          <SelectItem key={subj} value={subj}>
                            {subj}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Text Question Input */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Your Question
                    </label>
                    <Textarea
                      placeholder="Type your question here... (e.g., 'What is the derivative of x^2 + 3x - 5?')"
                      value={question}
                      onChange={(e) => setQuestion(e.target.value)}
                      rows={4}
                      className="resize-none"
                    />
                  </div>

                  {/* Image Upload Section */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Or Upload an Image
                    </label>
                    
                    {!imagePreview ? (
                      <div
                        onClick={() => fileInputRef.current?.click()}
                        className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-colors"
                      >
                        <Upload className="w-8 h-8 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-600 mb-2">Click to upload or drag and drop</p>
                        <p className="text-sm text-gray-500">PNG, JPG, GIF up to 5MB</p>
                      </div>
                    ) : (
                      <div className="relative rounded-lg overflow-hidden">
                        <img
                          src={imagePreview}
                          alt="Uploaded question"
                          className="w-full max-h-64 object-cover"
                        />
                        <button
                          type="button"
                          onClick={removeImage}
                          className="absolute top-2 right-2 w-8 h-8 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                    
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/*"
                      onChange={handleImageUpload}
                      className="hidden"
                    />
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-col sm:flex-row gap-3">
                    <Button
                      type="submit"
                      disabled={isLoading || (!question.trim() && !uploadedImage) || !subject}
                      className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Processing...
                        </>
                      ) : (
                        <>
                          <Send className="w-4 h-4 mr-2" />
                          Get Answer
                        </>
                      )}
                    </Button>
                    
                    <Button
                      type="button"
                      variant="outline"
                      onClick={resetForm}
                      disabled={isLoading}
                    >
                      Reset
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </motion.div>

          {/* Answer Section */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm h-full">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Sparkles className="w-5 h-5 text-purple-600" />
                  <span>AI Solution</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <AnimatePresence mode="wait">
                  {isLoading ? (
                    <motion.div
                      key="loading"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="flex flex-col items-center justify-center py-12"
                    >
                      <Loader2 className="w-12 h-12 text-blue-600 animate-spin mb-4" />
                      <p className="text-gray-600 text-center">
                        AI is analyzing your question...
                        <br />
                        <span className="text-sm">This usually takes a few seconds</span>
                      </p>
                    </motion.div>
                  ) : aiResponse ? (
                    <motion.div
                      key="response"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      className="space-y-6"
                    >
                      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-4 border border-green-200">
                        <h3 className="font-semibold text-green-800 mb-2 flex items-center">
                          <Sparkles className="w-4 h-4 mr-2" />
                          Solution
                        </h3>
                        <div className="text-gray-800 whitespace-pre-line">
                          {aiResponse.solution}
                        </div>
                      </div>

                      {aiResponse.steps && (
                        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                          <h3 className="font-semibold text-blue-800 mb-3">Steps:</h3>
                          <ol className="list-decimal list-inside space-y-2">
                            {aiResponse.steps.map((step, index) => (
                              <li key={index} className="text-gray-700">
                                {step}
                              </li>
                            ))}
                          </ol>
                        </div>
                      )}

                      <div className="flex justify-center">
                        <Button
                          onClick={() => navigate('/history')}
                          variant="outline"
                          className="flex items-center space-x-2"
                        >
                          <span>View in History</span>
                        </Button>
                      </div>
                    </motion.div>
                  ) : (
                    <motion.div
                      key="empty"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="flex flex-col items-center justify-center py-12 text-center"
                    >
                      <AlertCircle className="w-16 h-16 text-gray-300 mb-4" />
                      <p className="text-gray-500">
                        Your AI-generated solution will appear here
                      </p>
                      <p className="text-sm text-gray-400 mt-2">
                        Submit a question to get started!
                      </p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Demo Notice */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="mt-8 text-center"
        >
          <div className="inline-flex items-center px-4 py-2 bg-yellow-100 text-yellow-800 rounded-full text-sm">
            <AlertCircle className="w-4 h-4 mr-2" />
            Currently showing mock AI responses - Backend integration in progress
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default AskDoubePage;