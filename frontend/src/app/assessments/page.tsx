'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  AcademicCapIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowRightIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';
import { useStore } from '@/lib/store';
import { assessmentAPI } from '@/lib/api';
import toast from 'react-hot-toast';

interface Question {
  question_id: string;
  question_text: string;
  options: string[];
  skill: string;
  difficulty: string;
}

interface Assessment {
  assessment_id: string;
  total_questions: number;
  category: string;
  current_question: Question | null;
  status: string;
}

export default function AssessmentsPage() {
  const { user } = useStore();
  const [categories, setCategories] = useState<any[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<string>('');
  const [timeLeft, setTimeLeft] = useState(60);
  const [questionsAnswered, setQuestionsAnswered] = useState(0);
  const [results, setResults] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (assessment && currentQuestion && timeLeft > 0) {
      timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
    }
    return () => clearTimeout(timer);
  }, [timeLeft, assessment, currentQuestion]);

  const loadCategories = async () => {
    try {
      const response = await assessmentAPI.getCategories();
      setCategories(response.data.categories);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  const startAssessment = async () => {
    if (!selectedCategory || selectedSkills.length === 0) {
      toast.error('Please select a category and at least one skill');
      return;
    }

    setIsLoading(true);
    try {
      const response = await assessmentAPI.start({
        student_id: user?.student_id || 'demo_user',
        category: selectedCategory,
        skills: selectedSkills,
        questions_per_skill: 3
      });

      setAssessment(response.data);
      setCurrentQuestion(response.data.current_question);
      setTimeLeft(60);
      toast.success('Assessment started!');
    } catch (error) {
      toast.error('Failed to start assessment');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!assessment || !currentQuestion || !selectedAnswer) {
      toast.error('Please select an answer');
      return;
    }

    setIsLoading(true);
    try {
      const response = await assessmentAPI.submitAnswer(assessment.assessment_id, {
        question_id: currentQuestion.question_id,
        answer: selectedAnswer,
        time_taken_seconds: 60 - timeLeft
      });

      // Show feedback
      if (response.data.is_correct) {
        toast.success('Correct! 🎉');
      } else {
        toast.error(`Incorrect. The answer was: ${response.data.correct_answer}`);
      }

      setQuestionsAnswered(prev => prev + 1);

      // Move to next question or complete
      if (response.data.next_question) {
        setCurrentQuestion(response.data.next_question);
        setSelectedAnswer('');
        setTimeLeft(60);
      } else {
        // Complete assessment
        const resultsResponse = await assessmentAPI.complete(assessment.assessment_id);
        setResults(resultsResponse.data);
        setAssessment(null);
        setCurrentQuestion(null);
      }
    } catch (error) {
      toast.error('Failed to submit answer');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSkill = (skill: string) => {
    setSelectedSkills(prev =>
      prev.includes(skill)
        ? prev.filter(s => s !== skill)
        : [...prev, skill]
    );
  };

  // Results view
  if (results) {
    return (
      <div className="max-w-3xl mx-auto">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="card text-center"
        >
          <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <ChartBarIcon className="w-10 h-10 text-primary-600" />
          </div>
          
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Assessment Complete!</h1>
          <p className="text-gray-500 mb-6">Here's how you performed</p>

          <div className="text-5xl font-bold gradient-text mb-2">
            {results.score}%
          </div>
          <p className="text-gray-500 mb-8">
            {results.correct_answers} of {results.total_questions} correct
          </p>

          <div className="grid grid-cols-2 gap-4 mb-8">
            <div className="bg-green-50 rounded-xl p-4">
              <h3 className="font-semibold text-green-800 mb-2">Strengths</h3>
              <ul className="text-sm text-green-600 space-y-1">
                {results.strengths.map((s: string, i: number) => (
                  <li key={i}>✓ {s}</li>
                ))}
                {results.strengths.length === 0 && <li>Keep practicing!</li>}
              </ul>
            </div>
            <div className="bg-red-50 rounded-xl p-4">
              <h3 className="font-semibold text-red-800 mb-2">Areas to Improve</h3>
              <ul className="text-sm text-red-600 space-y-1">
                {results.weaknesses.map((w: string, i: number) => (
                  <li key={i}>• {w}</li>
                ))}
                {results.weaknesses.length === 0 && <li>Great job!</li>}
              </ul>
            </div>
          </div>

          <div className="bg-gray-50 rounded-xl p-4 mb-6 text-left">
            <h3 className="font-semibold text-gray-900 mb-2">AI Feedback</h3>
            <p className="text-sm text-gray-600">{results.feedback}</p>
          </div>

          <button
            onClick={() => setResults(null)}
            className="btn-primary"
          >
            Take Another Assessment
          </button>
        </motion.div>
      </div>
    );
  }

  // Assessment in progress
  if (assessment && currentQuestion) {
    return (
      <div className="max-w-3xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card"
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <span className="text-sm text-gray-500">
                Question {questionsAnswered + 1} of {assessment.total_questions}
              </span>
              <div className="flex items-center space-x-2 mt-1">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  currentQuestion.difficulty === 'easy' ? 'bg-green-100 text-green-700' :
                  currentQuestion.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-red-100 text-red-700'
                }`}>
                  {currentQuestion.difficulty}
                </span>
                <span className="text-sm text-gray-500">{currentQuestion.skill}</span>
              </div>
            </div>
            <div className={`flex items-center space-x-2 ${timeLeft < 15 ? 'text-red-500' : 'text-gray-500'}`}>
              <ClockIcon className="w-5 h-5" />
              <span className="font-mono text-lg">{timeLeft}s</span>
            </div>
          </div>

          {/* Progress bar */}
          <div className="h-2 bg-gray-100 rounded-full mb-6 overflow-hidden">
            <div
              className="h-full bg-primary-500 transition-all duration-300"
              style={{ width: `${(questionsAnswered / assessment.total_questions) * 100}%` }}
            />
          </div>

          {/* Question */}
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            {currentQuestion.question_text}
          </h2>

          {/* Options */}
          <div className="space-y-3 mb-6">
            {currentQuestion.options.map((option, index) => (
              <button
                key={index}
                onClick={() => setSelectedAnswer(option)}
                className={`w-full p-4 text-left rounded-xl border-2 transition-all ${
                  selectedAnswer === option
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <span className="font-medium">{String.fromCharCode(65 + index)}.</span> {option}
              </button>
            ))}
          </div>

          {/* Submit button */}
          <button
            onClick={submitAnswer}
            disabled={!selectedAnswer || isLoading}
            className="btn-primary w-full disabled:opacity-50"
          >
            {isLoading ? 'Submitting...' : 'Submit Answer'}
            <ArrowRightIcon className="w-5 h-5 ml-2 inline" />
          </button>
        </motion.div>
      </div>
    );
  }

  // Assessment selection
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Skill Assessment</h1>
        <p className="text-gray-500 mt-1">
          Test your skills with adaptive assessments that adjust to your level
        </p>
      </div>

      {/* Category Selection */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Category</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => {
                setSelectedCategory(category.id);
                setSelectedSkills([]);
              }}
              className={`p-4 rounded-xl border-2 text-left transition-all ${
                selectedCategory === category.id
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <AcademicCapIcon className="w-8 h-8 text-primary-500 mb-2" />
              <h3 className="font-semibold text-gray-900">{category.name}</h3>
              <p className="text-sm text-gray-500 mt-1">
                {category.skills.length} skills available
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Skills Selection */}
      {selectedCategory && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card"
        >
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Skills to Assess</h2>
          <div className="flex flex-wrap gap-3">
            {categories
              .find(c => c.id === selectedCategory)
              ?.skills.map((skill: string) => (
                <button
                  key={skill}
                  onClick={() => toggleSkill(skill)}
                  className={`px-4 py-2 rounded-full border-2 transition-all ${
                    selectedSkills.includes(skill)
                      ? 'border-primary-500 bg-primary-500 text-white'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  {skill.toUpperCase()}
                </button>
              ))}
          </div>
        </motion.div>
      )}

      {/* Start Button */}
      {selectedSkills.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card bg-gradient-to-r from-primary-600 to-primary-800 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold">Ready to Start?</h2>
              <p className="text-primary-100 mt-1">
                {selectedSkills.length} skill(s) selected • ~{selectedSkills.length * 3} questions
              </p>
            </div>
            <button
              onClick={startAssessment}
              disabled={isLoading}
              className="bg-white text-primary-600 px-6 py-3 rounded-xl font-semibold hover:bg-primary-50 transition-colors"
            >
              {isLoading ? 'Starting...' : 'Start Assessment'}
            </button>
          </div>
        </motion.div>
      )}
    </div>
  );
}
