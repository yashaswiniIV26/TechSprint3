'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  CalendarIcon,
  CheckCircleIcon,
  ClockIcon,
  BookOpenIcon,
  VideoCameraIcon,
  CodeBracketIcon,
  AcademicCapIcon,
  ChevronLeftIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';
import { useStore } from '@/lib/store';
import { roadmapAPI } from '@/lib/api';
import toast from 'react-hot-toast';

interface Task {
  task_id: string;
  title: string;
  description: string;
  resource_type: string;
  resource_url?: string;
  duration_minutes: number;
  completed: boolean;
}

interface DayPlan {
  day: number;
  date: string;
  tasks: Task[];
  focus_area: string;
}

interface WeekPlan {
  week: number;
  theme: string;
  days: DayPlan[];
  milestone: string;
}

interface Roadmap {
  roadmap_id: string;
  student_id: string;
  target_company?: string;
  target_role?: string;
  duration_weeks: number;
  current_week: number;
  progress: number;
  weeks: WeekPlan[];
  created_at: string;
}

export default function RoadmapPage() {
  const { user } = useStore();
  const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
  const [currentWeek, setCurrentWeek] = useState(1);
  const [todaysTasks, setTodaysTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationParams, setGenerationParams] = useState({
    duration_weeks: 12,
    daily_commitment: '2 hours',
    target_company: '',
    target_role: ''
  });

  useEffect(() => {
    loadRoadmap();
  }, []);

  const loadRoadmap = async () => {
    setIsLoading(true);
    try {
      const response = await roadmapAPI.getActive(user?.student_id || 'demo_user');
      if (response.data) {
        setRoadmap(response.data);
        setCurrentWeek(response.data.current_week || 1);
        // Load today's tasks
        const tasksResponse = await roadmapAPI.getTodaysTasks(response.data.roadmap_id);
        setTodaysTasks(tasksResponse.data.tasks || []);
      }
    } catch (error) {
      console.error('No active roadmap:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const generateRoadmap = async () => {
    setIsGenerating(true);
    try {
      const response = await roadmapAPI.generate({
        student_id: user?.student_id || 'demo_user',
        duration_weeks: generationParams.duration_weeks,
        daily_commitment: generationParams.daily_commitment,
        company_id: generationParams.target_company || undefined
      });
      setRoadmap(response.data);
      setCurrentWeek(1);
      toast.success('Roadmap generated successfully!');
    } catch (error) {
      toast.error('Failed to generate roadmap');
      console.error(error);
    } finally {
      setIsGenerating(false);
    }
  };

  const completeTask = async (taskId: string) => {
    if (!roadmap) return;
    
    try {
      await roadmapAPI.updateProgress(roadmap.roadmap_id, taskId);
      // Update local state
      setTodaysTasks(prev =>
        prev.map(task =>
          task.task_id === taskId ? { ...task, completed: true } : task
        )
      );
      toast.success('Task completed!');
    } catch (error) {
      toast.error('Failed to update progress');
      console.error(error);
    }
  };

  const getResourceIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'video': return <VideoCameraIcon className="w-5 h-5" />;
      case 'article': return <BookOpenIcon className="w-5 h-5" />;
      case 'practice': return <CodeBracketIcon className="w-5 h-5" />;
      default: return <AcademicCapIcon className="w-5 h-5" />;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  // No roadmap - show generation form
  if (!roadmap) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="text-center">
          <CalendarIcon className="w-16 h-16 text-primary-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900">Generate Your Learning Roadmap</h1>
          <p className="text-gray-500 mt-2">
            Create a personalized study plan based on your goals and skill gaps
          </p>
        </div>

        <div className="card space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Duration (weeks)
            </label>
            <select
              value={generationParams.duration_weeks}
              onChange={(e) => setGenerationParams(prev => ({
                ...prev,
                duration_weeks: parseInt(e.target.value)
              }))}
              className="input-field"
            >
              <option value={4}>4 weeks (Intensive)</option>
              <option value={8}>8 weeks (Standard)</option>
              <option value={12}>12 weeks (Comprehensive)</option>
              <option value={16}>16 weeks (Relaxed)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Daily Commitment
            </label>
            <select
              value={generationParams.daily_commitment}
              onChange={(e) => setGenerationParams(prev => ({
                ...prev,
                daily_commitment: e.target.value
              }))}
              className="input-field"
            >
              <option value="1 hour">1 hour/day</option>
              <option value="2 hours">2 hours/day</option>
              <option value="3 hours">3 hours/day</option>
              <option value="4 hours">4+ hours/day</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target Company (optional)
            </label>
            <input
              type="text"
              value={generationParams.target_company}
              onChange={(e) => setGenerationParams(prev => ({
                ...prev,
                target_company: e.target.value
              }))}
              placeholder="e.g., Google, Amazon, Microsoft"
              className="input-field"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target Role (optional)
            </label>
            <input
              type="text"
              value={generationParams.target_role}
              onChange={(e) => setGenerationParams(prev => ({
                ...prev,
                target_role: e.target.value
              }))}
              placeholder="e.g., Software Engineer, Data Scientist"
              className="input-field"
            />
          </div>

          <button
            onClick={generateRoadmap}
            disabled={isGenerating}
            className="btn-primary w-full"
          >
            {isGenerating ? 'Generating...' : 'Generate Personalized Roadmap'}
          </button>
        </div>
      </div>
    );
  }

  // Show roadmap
  const weekData = roadmap.weeks?.find(w => w.week === currentWeek);

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Your Learning Roadmap</h1>
          <p className="text-gray-500 mt-1">
            {roadmap.target_company && `Targeting ${roadmap.target_company}`}
            {roadmap.target_role && ` • ${roadmap.target_role}`}
          </p>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold gradient-text">{roadmap.progress || 0}%</div>
          <div className="text-sm text-gray-500">Overall Progress</div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="card">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">
            Week {currentWeek} of {roadmap.duration_weeks}
          </span>
          <span className="text-sm text-gray-500">
            {roadmap.progress || 0}% Complete
          </span>
        </div>
        <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-primary-500 to-accent-500 transition-all duration-500"
            style={{ width: `${roadmap.progress || 0}%` }}
          />
        </div>
      </div>

      {/* Today's Tasks */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <ClockIcon className="w-5 h-5 mr-2 text-primary-500" />
          Today's Tasks
        </h2>
        {todaysTasks.length > 0 ? (
          <div className="space-y-3">
            {todaysTasks.map((task) => (
              <motion.div
                key={task.task_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className={`p-4 rounded-xl border ${
                  task.completed
                    ? 'bg-green-50 border-green-200'
                    : 'bg-white border-gray-200 hover:border-primary-300'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <button
                      onClick={() => !task.completed && completeTask(task.task_id)}
                      className={`mt-1 ${task.completed ? 'text-green-500' : 'text-gray-300 hover:text-primary-500'}`}
                    >
                      <CheckCircleIcon className="w-6 h-6" />
                    </button>
                    <div>
                      <h3 className={`font-medium ${task.completed ? 'text-green-700 line-through' : 'text-gray-900'}`}>
                        {task.title}
                      </h3>
                      <p className="text-sm text-gray-500 mt-1">{task.description}</p>
                      <div className="flex items-center space-x-4 mt-2">
                        <span className="flex items-center text-sm text-gray-400">
                          {getResourceIcon(task.resource_type)}
                          <span className="ml-1 capitalize">{task.resource_type}</span>
                        </span>
                        <span className="flex items-center text-sm text-gray-400">
                          <ClockIcon className="w-4 h-4 mr-1" />
                          {task.duration_minutes} min
                        </span>
                      </div>
                    </div>
                  </div>
                  {task.resource_url && (
                    <a
                      href={task.resource_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary-500 hover:text-primary-700 text-sm font-medium"
                    >
                      Open →
                    </a>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">No tasks for today. Great job!</p>
        )}
      </div>

      {/* Weekly View */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">
            Week {currentWeek}: {weekData?.theme || 'Loading...'}
          </h2>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setCurrentWeek(prev => Math.max(1, prev - 1))}
              disabled={currentWeek === 1}
              className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50"
            >
              <ChevronLeftIcon className="w-5 h-5" />
            </button>
            <button
              onClick={() => setCurrentWeek(prev => Math.min(roadmap.duration_weeks, prev + 1))}
              disabled={currentWeek === roadmap.duration_weeks}
              className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50"
            >
              <ChevronRightIcon className="w-5 h-5" />
            </button>
          </div>
        </div>

        {weekData?.milestone && (
          <div className="bg-accent-50 border border-accent-200 rounded-xl p-4 mb-4">
            <div className="flex items-center">
              <AcademicCapIcon className="w-5 h-5 text-accent-600 mr-2" />
              <span className="font-medium text-accent-700">Milestone: {weekData.milestone}</span>
            </div>
          </div>
        )}

        {weekData?.days && (
          <div className="grid grid-cols-7 gap-2">
            {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, index) => {
              const dayPlan = weekData.days[index];
              const completedTasks = dayPlan?.tasks?.filter(t => t.completed).length || 0;
              const totalTasks = dayPlan?.tasks?.length || 0;
              
              return (
                <div
                  key={day}
                  className="bg-gray-50 rounded-xl p-3 text-center"
                >
                  <div className="text-sm font-medium text-gray-700">{day}</div>
                  <div className="text-xs text-gray-400 mt-1">
                    {dayPlan?.focus_area || 'Rest'}
                  </div>
                  {totalTasks > 0 && (
                    <div className="mt-2">
                      <div className="h-1 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary-500"
                          style={{ width: `${(completedTasks / totalTasks) * 100}%` }}
                        />
                      </div>
                      <div className="text-xs text-gray-400 mt-1">
                        {completedTasks}/{totalTasks}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
