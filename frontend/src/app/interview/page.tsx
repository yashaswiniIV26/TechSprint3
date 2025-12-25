'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MicrophoneIcon,
  StopIcon,
  ChatBubbleLeftRightIcon,
  UserCircleIcon,
  SparklesIcon,
  ClockIcon,
  PlayIcon,
  PauseIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { useStore } from '@/lib/store';
import { interviewAPI } from '@/lib/api';
import toast from 'react-hot-toast';

interface Message {
  id: string;
  role: 'interviewer' | 'user';
  content: string;
  timestamp: Date;
  feedback?: {
    score: number;
    suggestions: string[];
  };
}

interface InterviewSession {
  session_id: string;
  interview_type: string;
  status: string;
  messages: Message[];
  current_question?: string;
}

const interviewTypes = [
  { id: 'technical', name: 'Technical Interview', icon: '💻', description: 'DSA, System Design, Coding' },
  { id: 'hr', name: 'HR Interview', icon: '👔', description: 'Behavioral, Situational questions' },
  { id: 'behavioral', name: 'Behavioral', icon: '🧠', description: 'STAR method, past experiences' },
  { id: 'system_design', name: 'System Design', icon: '📊', description: 'Architecture & Problem-solving' },
];

const languages = [
  { code: 'en', name: 'English' },
  { code: 'hi', name: 'Hindi' },
  { code: 'ta', name: 'Tamil' },
  { code: 'te', name: 'Telugu' },
  { code: 'bn', name: 'Bengali' },
  { code: 'mr', name: 'Marathi' },
];

export default function InterviewCoachPage() {
  const { user } = useStore();
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [selectedType, setSelectedType] = useState<string>('');
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [targetCompany, setTargetCompany] = useState('');
  const [targetRole, setTargetRole] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [sessionTime, setSessionTime] = useState(0);
  const [sessionActive, setSessionActive] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (sessionActive) {
      timerRef.current = setInterval(() => {
        setSessionTime(prev => prev + 1);
      }, 1000);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [sessionActive]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const startInterview = async () => {
    if (!selectedType) {
      toast.error('Please select an interview type');
      return;
    }

    setIsLoading(true);
    try {
      const response = await interviewAPI.start({
        student_id: user?.student_id || 'demo_user',
        interview_type: selectedType,
        language: selectedLanguage,
        target_company: targetCompany || undefined,
        target_role: targetRole || undefined
      });

      setSession(response.data);
      setSessionActive(true);
      setSessionTime(0);

      // Add initial interviewer message
      if (response.data.current_question) {
        setMessages([{
          id: Date.now().toString(),
          role: 'interviewer',
          content: response.data.current_question,
          timestamp: new Date()
        }]);
      }

      toast.success('Interview started!');
    } catch (error) {
      toast.error('Failed to start interview');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const sendResponse = async () => {
    if (!session || !inputText.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputText,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await interviewAPI.respond(session.session_id, {
        response_text: inputText,
        response_type: 'text'
      });

      // Add interviewer response with feedback
      const interviewerMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'interviewer',
        content: response.data.next_question || response.data.feedback?.overall_feedback || 'Thank you for your response.',
        timestamp: new Date(),
        feedback: response.data.feedback ? {
          score: response.data.feedback.score || 0,
          suggestions: response.data.feedback.suggestions || []
        } : undefined
      };

      setMessages(prev => [...prev, interviewerMessage]);

      if (response.data.session_ended) {
        setSessionActive(false);
        toast.success('Interview completed!');
      }
    } catch (error) {
      toast.error('Failed to send response');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const endInterview = async () => {
    if (!session) return;

    try {
      const response = await interviewAPI.end(session.session_id);
      setSessionActive(false);
      toast.success('Interview ended. Check your feedback!');
    } catch (error) {
      toast.error('Failed to end interview');
      console.error(error);
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      setIsRecording(false);
      // Stop recording logic - would integrate with Web Speech API
      toast('Recording stopped');
    } else {
      setIsRecording(true);
      toast('Recording started...');
      // Start recording logic
    }
  };

  const resetSession = () => {
    setSession(null);
    setMessages([]);
    setSessionTime(0);
    setSessionActive(false);
    setSelectedType('');
  };

  // Interview selection screen
  if (!session) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="text-center">
          <ChatBubbleLeftRightIcon className="w-16 h-16 text-primary-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900">AI Interview Coach</h1>
          <p className="text-gray-500 mt-2">
            Practice interviews with AI that adapts to your responses and provides real-time feedback
          </p>
        </div>

        {/* Interview Type Selection */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Interview Type</h2>
          <div className="grid grid-cols-2 gap-4">
            {interviewTypes.map((type) => (
              <button
                key={type.id}
                onClick={() => setSelectedType(type.id)}
                className={`p-4 rounded-xl border-2 text-left transition-all ${
                  selectedType === type.id
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="text-3xl mb-2">{type.icon}</div>
                <h3 className="font-semibold text-gray-900">{type.name}</h3>
                <p className="text-sm text-gray-500 mt-1">{type.description}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Language Selection */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Language</h2>
          <div className="flex flex-wrap gap-3">
            {languages.map((lang) => (
              <button
                key={lang.code}
                onClick={() => setSelectedLanguage(lang.code)}
                className={`px-4 py-2 rounded-full border-2 transition-all ${
                  selectedLanguage === lang.code
                    ? 'border-primary-500 bg-primary-500 text-white'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                {lang.name}
              </button>
            ))}
          </div>
        </div>

        {/* Target Company/Role */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Target (Optional)</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Company</label>
              <input
                type="text"
                value={targetCompany}
                onChange={(e) => setTargetCompany(e.target.value)}
                placeholder="e.g., Google"
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
              <input
                type="text"
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                placeholder="e.g., Software Engineer"
                className="input-field"
              />
            </div>
          </div>
        </div>

        {/* Start Button */}
        {selectedType && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <button
              onClick={startInterview}
              disabled={isLoading}
              className="btn-primary w-full py-4 text-lg"
            >
              {isLoading ? 'Starting...' : 'Start Interview'}
            </button>
          </motion.div>
        )}
      </div>
    );
  }

  // Active interview screen
  return (
    <div className="h-[calc(100vh-12rem)] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-accent-500 rounded-full flex items-center justify-center">
            <SparklesIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-semibold text-gray-900">AI Interviewer</h1>
            <p className="text-sm text-gray-500 capitalize">
              {selectedType.replace('_', ' ')} Interview
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 px-4 py-2 bg-gray-100 rounded-full">
            <ClockIcon className="w-5 h-5 text-gray-500" />
            <span className="font-mono text-gray-700">{formatTime(sessionTime)}</span>
          </div>
          <button
            onClick={endInterview}
            className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
          >
            End Interview
          </button>
          <button
            onClick={resetSession}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <ArrowPathIcon className="w-5 h-5 text-gray-500" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto bg-gray-50 rounded-xl p-4 space-y-4">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[70%] ${message.role === 'user' ? 'order-2' : 'order-1'}`}>
                <div
                  className={`p-4 rounded-2xl ${
                    message.role === 'user'
                      ? 'bg-primary-500 text-white rounded-br-md'
                      : 'bg-white text-gray-900 rounded-bl-md shadow-sm'
                  }`}
                >
                  <p>{message.content}</p>
                </div>
                
                {/* Feedback for user responses */}
                {message.role === 'interviewer' && message.feedback && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-green-800">Response Score</span>
                      <span className="text-lg font-bold text-green-600">{message.feedback.score}/10</span>
                    </div>
                    {message.feedback.suggestions.length > 0 && (
                      <div className="text-sm text-green-700">
                        <span className="font-medium">Tips: </span>
                        {message.feedback.suggestions.join(' • ')}
                      </div>
                    )}
                  </motion.div>
                )}
                
                <div className={`text-xs text-gray-400 mt-1 ${message.role === 'user' ? 'text-right' : ''}`}>
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
              
              <div className={`w-8 h-8 rounded-full flex items-center justify-center mx-2 ${
                message.role === 'user' ? 'order-1 bg-gray-200' : 'order-2 bg-primary-100'
              }`}>
                {message.role === 'user' ? (
                  <UserCircleIcon className="w-5 h-5 text-gray-500" />
                ) : (
                  <SparklesIcon className="w-5 h-5 text-primary-500" />
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start"
          >
            <div className="bg-white p-4 rounded-2xl rounded-bl-md shadow-sm">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
            </div>
          </motion.div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="mt-4 bg-white rounded-xl border border-gray-200 p-4">
        <div className="flex items-end space-x-4">
          <div className="flex-1">
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendResponse();
                }
              }}
              placeholder="Type your response..."
              rows={2}
              className="w-full resize-none border-0 focus:ring-0 text-gray-900 placeholder-gray-400"
            />
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={toggleRecording}
              className={`p-3 rounded-full transition-all ${
                isRecording
                  ? 'bg-red-500 text-white animate-pulse'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {isRecording ? (
                <StopIcon className="w-6 h-6" />
              ) : (
                <MicrophoneIcon className="w-6 h-6" />
              )}
            </button>
            <button
              onClick={sendResponse}
              disabled={!inputText.trim() || isLoading}
              className="btn-primary px-6 py-3 disabled:opacity-50"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
