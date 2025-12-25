'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  UserGroupIcon,
  ChartBarIcon,
  SparklesIcon,
  ArrowTrendingUpIcon,
  ClockIcon,
  BookOpenIcon,
  AcademicCapIcon,
  LightBulbIcon,
  BeakerIcon
} from '@heroicons/react/24/outline';
import { useStore } from '@/lib/store';
import { digitalTwinAPI } from '@/lib/api';
import toast from 'react-hot-toast';

interface Prediction {
  metric: string;
  current_value: number;
  predicted_value: number;
  timeframe: string;
  confidence: number;
}

interface Pattern {
  pattern_type: string;
  description: string;
  frequency: string;
  impact: string;
}

interface Insight {
  category: string;
  title: string;
  description: string;
  action_item: string;
  priority: string;
}

interface DigitalTwin {
  twin_id: string;
  student_id: string;
  success_probability: number;
  predictions: Prediction[];
  patterns: Pattern[];
  insights: Insight[];
  last_updated: string;
}

export default function DigitalTwinPage() {
  const { user } = useStore();
  const [digitalTwin, setDigitalTwin] = useState<DigitalTwin | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'predictions' | 'patterns' | 'insights'>('overview');

  useEffect(() => {
    loadDigitalTwin();
  }, []);

  const loadDigitalTwin = async () => {
    setIsLoading(true);
    try {
      const response = await digitalTwinAPI.get(user?.student_id || 'demo_user');
      setDigitalTwin(response.data);
    } catch (error) {
      console.error('Error loading digital twin:', error);
      // Create if doesn't exist
      try {
        const createResponse = await digitalTwinAPI.create(user?.student_id || 'demo_user');
        setDigitalTwin(createResponse.data);
      } catch (createError) {
        console.error('Error creating digital twin:', createError);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const getPredictions = async () => {
    try {
      const response = await digitalTwinAPI.getPredictions(user?.student_id || 'demo_user');
      if (response.data.predictions) {
        setDigitalTwin(prev => prev ? { ...prev, predictions: response.data.predictions } : null);
      }
      toast.success('Predictions updated!');
    } catch (error) {
      toast.error('Failed to get predictions');
      console.error(error);
    }
  };

  const getInsights = async () => {
    try {
      const response = await digitalTwinAPI.getInsights(user?.student_id || 'demo_user');
      if (response.data.insights) {
        setDigitalTwin(prev => prev ? { ...prev, insights: response.data.insights } : null);
      }
      toast.success('Insights updated!');
    } catch (error) {
      toast.error('Failed to get insights');
      console.error(error);
    }
  };

  const getPatterns = async () => {
    try {
      const response = await digitalTwinAPI.getPatterns(user?.student_id || 'demo_user');
      if (response.data.patterns) {
        setDigitalTwin(prev => prev ? { ...prev, patterns: response.data.patterns } : null);
      }
      toast.success('Patterns analyzed!');
    } catch (error) {
      toast.error('Failed to get patterns');
      console.error(error);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high': return 'bg-red-100 text-red-700 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-700 border-green-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact.toLowerCase()) {
      case 'positive': return 'text-green-600';
      case 'negative': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <div className="relative">
          <div className="w-20 h-20 border-4 border-primary-200 rounded-full animate-spin border-t-primary-600"></div>
          <div className="absolute inset-0 flex items-center justify-center">
            <SparklesIcon className="w-8 h-8 text-primary-600" />
          </div>
        </div>
        <p className="mt-4 text-gray-500">Loading your Digital Twin...</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <UserGroupIcon className="w-8 h-8 mr-3 text-primary-500" />
            Your Digital Twin
          </h1>
          <p className="text-gray-500 mt-1">
            AI-powered predictions and insights based on your learning patterns
          </p>
        </div>
      </div>

      {/* Success Probability Card */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="card bg-gradient-to-r from-primary-600 via-primary-700 to-accent-600 text-white overflow-hidden relative"
      >
        <div className="absolute right-0 top-0 w-64 h-64 bg-white/10 rounded-full -mr-32 -mt-32" />
        <div className="absolute left-0 bottom-0 w-48 h-48 bg-white/10 rounded-full -ml-24 -mb-24" />
        
        <div className="relative z-10 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold opacity-90">Placement Success Probability</h2>
            <p className="text-sm text-white/70 mt-1">
              Based on your current progress and learning patterns
            </p>
          </div>
          <div className="text-right">
            <div className="text-6xl font-bold">{digitalTwin?.success_probability || 0}%</div>
            <div className="text-sm text-white/70 mt-1">
              Last updated: {digitalTwin?.last_updated ? new Date(digitalTwin.last_updated).toLocaleDateString() : 'N/A'}
            </div>
          </div>
        </div>
        
        <div className="relative z-10 mt-6 pt-6 border-t border-white/20 grid grid-cols-3 gap-4">
          <button
            onClick={getPredictions}
            className="bg-white/20 hover:bg-white/30 rounded-xl p-4 text-center transition-colors"
          >
            <ArrowTrendingUpIcon className="w-6 h-6 mx-auto mb-2" />
            <span className="text-sm font-medium">Update Predictions</span>
          </button>
          <button
            onClick={getPatterns}
            className="bg-white/20 hover:bg-white/30 rounded-xl p-4 text-center transition-colors"
          >
            <ChartBarIcon className="w-6 h-6 mx-auto mb-2" />
            <span className="text-sm font-medium">Analyze Patterns</span>
          </button>
          <button
            onClick={getInsights}
            className="bg-white/20 hover:bg-white/30 rounded-xl p-4 text-center transition-colors"
          >
            <LightBulbIcon className="w-6 h-6 mx-auto mb-2" />
            <span className="text-sm font-medium">Get Insights</span>
          </button>
        </div>
      </motion.div>

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-gray-200">
        {(['overview', 'predictions', 'patterns', 'insights'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 font-medium capitalize transition-colors ${
              activeTab === tab
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid md:grid-cols-2 gap-6">
          {/* Quick Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <BeakerIcon className="w-5 h-5 mr-2 text-primary-500" />
              Learning Profile
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-600">Learning Consistency</span>
                <span className="font-semibold text-gray-900">85%</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-600">Skill Acquisition Rate</span>
                <span className="font-semibold text-gray-900">+2.3/week</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-600">Practice Sessions</span>
                <span className="font-semibold text-gray-900">24 this month</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-600">Average Session Duration</span>
                <span className="font-semibold text-gray-900">45 min</span>
              </div>
            </div>
          </motion.div>

          {/* Top Predictions Preview */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <ArrowTrendingUpIcon className="w-5 h-5 mr-2 text-primary-500" />
              Key Predictions
            </h3>
            <div className="space-y-4">
              {(digitalTwin?.predictions || []).slice(0, 3).map((prediction, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-gray-900">{prediction.metric}</span>
                    <span className="text-sm text-gray-500">{prediction.timeframe}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-gray-500">{prediction.current_value}%</span>
                    <ArrowTrendingUpIcon className="w-4 h-4 text-green-500" />
                    <span className="font-semibold text-green-600">{prediction.predicted_value}%</span>
                  </div>
                </div>
              ))}
              {(!digitalTwin?.predictions || digitalTwin.predictions.length === 0) && (
                <p className="text-gray-400 text-center py-4">Click "Update Predictions" to generate forecasts</p>
              )}
            </div>
          </motion.div>
        </div>
      )}

      {activeTab === 'predictions' && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Predictions</h3>
          {(digitalTwin?.predictions || []).length > 0 ? (
            <div className="space-y-4">
              {digitalTwin?.predictions.map((prediction, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 bg-gray-50 rounded-xl"
                >
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-gray-900">{prediction.metric}</h4>
                    <span className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm">
                      {prediction.timeframe}
                    </span>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="flex-1">
                      <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                        <div className="h-full bg-gray-400" style={{ width: `${prediction.current_value}%` }} />
                      </div>
                      <div className="text-sm text-gray-500 mt-1">Current: {prediction.current_value}%</div>
                    </div>
                    <ArrowTrendingUpIcon className="w-6 h-6 text-green-500" />
                    <div className="flex-1">
                      <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                        <div className="h-full bg-green-500" style={{ width: `${prediction.predicted_value}%` }} />
                      </div>
                      <div className="text-sm text-green-600 mt-1">Predicted: {prediction.predicted_value}%</div>
                    </div>
                  </div>
                  <div className="mt-2 text-sm text-gray-500">
                    Confidence: {prediction.confidence}%
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <ArrowTrendingUpIcon className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No predictions yet</p>
              <button onClick={getPredictions} className="btn-primary mt-4">
                Generate Predictions
              </button>
            </div>
          )}
        </div>
      )}

      {activeTab === 'patterns' && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Learning Patterns</h3>
          {(digitalTwin?.patterns || []).length > 0 ? (
            <div className="space-y-4">
              {digitalTwin?.patterns.map((pattern, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 bg-gray-50 rounded-xl"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="px-2 py-1 bg-primary-100 text-primary-700 rounded text-xs font-medium">
                        {pattern.pattern_type}
                      </span>
                      <p className="mt-2 text-gray-900">{pattern.description}</p>
                      <p className="text-sm text-gray-500 mt-1">Frequency: {pattern.frequency}</p>
                    </div>
                    <span className={`text-sm font-medium ${getImpactColor(pattern.impact)}`}>
                      {pattern.impact} impact
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <ChartBarIcon className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No patterns analyzed yet</p>
              <button onClick={getPatterns} className="btn-primary mt-4">
                Analyze Patterns
              </button>
            </div>
          )}
        </div>
      )}

      {activeTab === 'insights' && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Insights</h3>
          {(digitalTwin?.insights || []).length > 0 ? (
            <div className="space-y-4">
              {digitalTwin?.insights.map((insight, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 bg-gray-50 rounded-xl"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="px-2 py-1 bg-gray-200 text-gray-700 rounded text-xs font-medium">
                        {insight.category}
                      </span>
                      <h4 className="font-semibold text-gray-900">{insight.title}</h4>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs font-medium border ${getPriorityColor(insight.priority)}`}>
                      {insight.priority}
                    </span>
                  </div>
                  <p className="text-gray-600">{insight.description}</p>
                  <div className="mt-3 p-3 bg-primary-50 rounded-lg">
                    <span className="text-sm font-medium text-primary-800">💡 Action: </span>
                    <span className="text-sm text-primary-700">{insight.action_item}</span>
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <LightBulbIcon className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No insights generated yet</p>
              <button onClick={getInsights} className="btn-primary mt-4">
                Generate Insights
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
