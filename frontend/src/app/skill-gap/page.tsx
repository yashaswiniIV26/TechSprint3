'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  BuildingOffice2Icon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ArrowTrendingUpIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';
import { useStore } from '@/lib/store';
import { skillGapAPI } from '@/lib/api';
import toast from 'react-hot-toast';

interface SkillGap {
  skill: string;
  current_level: number;
  required_level: number;
  gap: number;
  priority: string;
}

interface Analysis {
  analysis_id: string;
  company: string;
  role: string;
  overall_match: number;
  skill_gaps: SkillGap[];
  recommendations: string[];
  created_at: string;
}

const companies = [
  { id: 'google', name: 'Google', logo: '🔍' },
  { id: 'amazon', name: 'Amazon', logo: '📦' },
  { id: 'microsoft', name: 'Microsoft', logo: '💻' },
  { id: 'meta', name: 'Meta', logo: '👤' },
  { id: 'apple', name: 'Apple', logo: '🍎' },
  { id: 'netflix', name: 'Netflix', logo: '🎬' },
  { id: 'tcs', name: 'TCS', logo: '🏢' },
  { id: 'infosys', name: 'Infosys', logo: '🏛️' },
];

const roles = [
  'Software Engineer',
  'Frontend Developer',
  'Backend Developer',
  'Full Stack Developer',
  'Data Scientist',
  'ML Engineer',
  'DevOps Engineer',
  'Product Manager'
];

export default function SkillGapPage() {
  const { user } = useStore();
  const [selectedCompany, setSelectedCompany] = useState<string>('');
  const [selectedRole, setSelectedRole] = useState<string>('');
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [history, setHistory] = useState<Analysis[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const response = await skillGapAPI.getHistory(user?.student_id || 'demo_user');
      setHistory(response.data.analyses || []);
    } catch (error) {
      console.error('Error loading history:', error);
    }
  };

  const analyzeGaps = async () => {
    if (!selectedCompany || !selectedRole) {
      toast.error('Please select a company and role');
      return;
    }

    setIsLoading(true);
    try {
      const response = await skillGapAPI.analyze({
        student_id: user?.student_id || 'demo_user',
        target_company: selectedCompany,
        target_role: selectedRole
      });
      setAnalysis(response.data);
      toast.success('Analysis complete!');
      await loadHistory();
    } catch (error) {
      toast.error('Failed to analyze skill gaps');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'critical': return 'bg-red-100 text-red-700 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-700 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-700 border-green-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getMatchColor = (match: number) => {
    if (match >= 80) return 'text-green-600';
    if (match >= 60) return 'text-yellow-600';
    if (match >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Skill Gap Analysis</h1>
        <p className="text-gray-500 mt-1">
          Identify gaps between your skills and company requirements
        </p>
      </div>

      {/* Company Selection */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Target Company</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {companies.map((company) => (
            <button
              key={company.id}
              onClick={() => setSelectedCompany(company.id)}
              className={`p-4 rounded-xl border-2 text-center transition-all ${
                selectedCompany === company.id
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="text-3xl mb-2">{company.logo}</div>
              <div className="font-medium text-gray-900">{company.name}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Role Selection */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Target Role</h2>
        <div className="flex flex-wrap gap-3">
          {roles.map((role) => (
            <button
              key={role}
              onClick={() => setSelectedRole(role)}
              className={`px-4 py-2 rounded-full border-2 transition-all ${
                selectedRole === role
                  ? 'border-primary-500 bg-primary-500 text-white'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              {role}
            </button>
          ))}
        </div>
      </div>

      {/* Analyze Button */}
      {selectedCompany && selectedRole && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card bg-gradient-to-r from-primary-600 to-primary-800 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold">Ready to Analyze?</h2>
              <p className="text-primary-100 mt-1">
                Analyzing gaps for {selectedRole} at {companies.find(c => c.id === selectedCompany)?.name}
              </p>
            </div>
            <button
              onClick={analyzeGaps}
              disabled={isLoading}
              className="bg-white text-primary-600 px-6 py-3 rounded-xl font-semibold hover:bg-primary-50 transition-colors flex items-center space-x-2"
            >
              <MagnifyingGlassIcon className="w-5 h-5" />
              <span>{isLoading ? 'Analyzing...' : 'Analyze Gaps'}</span>
            </button>
          </div>
        </motion.div>
      )}

      {/* Analysis Results */}
      {analysis && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Overall Match Score */}
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Overall Match Score</h2>
                <p className="text-gray-500">{analysis.role} at {analysis.company}</p>
              </div>
              <div className={`text-5xl font-bold ${getMatchColor(analysis.overall_match)}`}>
                {analysis.overall_match}%
              </div>
            </div>
            
            <div className="h-4 bg-gray-100 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-1000 ${
                  analysis.overall_match >= 80 ? 'bg-green-500' :
                  analysis.overall_match >= 60 ? 'bg-yellow-500' :
                  analysis.overall_match >= 40 ? 'bg-orange-500' :
                  'bg-red-500'
                }`}
                style={{ width: `${analysis.overall_match}%` }}
              />
            </div>
          </div>

          {/* Skill Gaps */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Skill Gaps</h2>
            <div className="space-y-4">
              {analysis.skill_gaps.map((gap, index) => (
                <motion.div
                  key={gap.skill}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-gray-50 rounded-xl p-4"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <span className="font-medium text-gray-900">{gap.skill}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getPriorityColor(gap.priority)}`}>
                        {gap.priority}
                      </span>
                    </div>
                    <div className="text-sm text-gray-500">
                      Gap: {gap.gap}%
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div className="flex-1">
                      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary-500"
                          style={{ width: `${gap.current_level}%` }}
                        />
                      </div>
                    </div>
                    <div className="text-sm text-gray-500 w-32 text-right">
                      {gap.current_level}% / {gap.required_level}%
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Recommendations */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <ArrowTrendingUpIcon className="w-5 h-5 mr-2" />
              Recommendations
            </h2>
            <div className="space-y-3">
              {analysis.recommendations.map((rec, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg"
                >
                  <CheckCircleIcon className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <p className="text-gray-700">{rec}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {/* History */}
      {history.length > 0 && !analysis && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Previous Analyses</h2>
          <div className="space-y-3">
            {history.slice(0, 5).map((item, index) => (
              <button
                key={item.analysis_id || index}
                onClick={() => setAnalysis(item)}
                className="w-full p-4 rounded-xl border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-all text-left"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-gray-900">{item.role}</div>
                    <div className="text-sm text-gray-500">{item.company}</div>
                  </div>
                  <div className={`text-2xl font-bold ${getMatchColor(item.overall_match)}`}>
                    {item.overall_match}%
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
