'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { 
  AcademicCapIcon, 
  ChartBarIcon, 
  MapIcon,
  ChatBubbleLeftRightIcon,
  SparklesIcon,
  ArrowTrendingUpIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { useStore } from '@/lib/store';

// Dashboard component
export default function Dashboard() {
  const { user } = useStore();
  const [stats, setStats] = useState({
    readinessScore: 62,
    assessmentsCompleted: 3,
    interviewsPracticed: 2,
    tasksToday: 5,
    tasksCompleted: 2
  });

  const quickActions = [
    {
      title: 'Take Assessment',
      description: 'Test your technical skills',
      icon: AcademicCapIcon,
      href: '/assessments',
      color: 'bg-blue-500',
    },
    {
      title: 'View Skill Gap',
      description: 'Compare with companies',
      icon: ChartBarIcon,
      href: '/skill-gap',
      color: 'bg-purple-500',
    },
    {
      title: 'My Roadmap',
      description: "Today's learning tasks",
      icon: MapIcon,
      href: '/roadmap',
      color: 'bg-green-500',
    },
    {
      title: 'Practice Interview',
      description: 'AI mock interview',
      icon: ChatBubbleLeftRightIcon,
      href: '/interview',
      color: 'bg-orange-500',
    },
  ];

  const recentActivity = [
    { type: 'assessment', title: 'Completed DSA Assessment', score: '78%', time: '2 hours ago' },
    { type: 'interview', title: 'Mock Technical Interview', score: '7.2/10', time: '1 day ago' },
    { type: 'roadmap', title: 'Completed Java Basics', time: '2 days ago' },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-2xl p-6 text-white"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Welcome back, {user?.name || 'Student'}! 👋</h1>
            <p className="mt-1 text-primary-100">
              Ready to continue your placement preparation journey?
            </p>
          </div>
          <div className="hidden md:block">
            <div className="text-center">
              <div className="text-4xl font-bold">{stats.readinessScore}%</div>
              <div className="text-primary-100 text-sm">Readiness Score</div>
            </div>
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-4">
          <div className="flex justify-between text-sm mb-1">
            <span>Overall Progress</span>
            <span>{stats.readinessScore}%</span>
          </div>
          <div className="h-2 bg-primary-900/30 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${stats.readinessScore}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
              className="h-full bg-white rounded-full"
            />
          </div>
        </div>
      </motion.div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action, index) => (
            <motion.div
              key={action.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Link href={action.href}>
                <div className="card hover:scale-105 cursor-pointer group">
                  <div className={`w-12 h-12 ${action.color} rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                    <action.icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="font-semibold text-gray-900">{action.title}</h3>
                  <p className="text-sm text-gray-500 mt-1">{action.description}</p>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Today's Tasks */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Today's Tasks</h2>
              <Link href="/roadmap" className="text-primary-600 text-sm hover:underline">
                View All
              </Link>
            </div>

            <div className="space-y-3">
              {[
                { title: 'Complete Python DSA problems', duration: '2 hrs', completed: true },
                { title: 'Watch System Design video', duration: '1 hr', completed: true },
                { title: 'Practice SQL queries', duration: '1 hr', completed: false },
                { title: 'Mock interview practice', duration: '30 min', completed: false },
                { title: 'Review OOPS concepts', duration: '45 min', completed: false },
              ].map((task, index) => (
                <div
                  key={index}
                  className={`flex items-center justify-between p-3 rounded-xl ${
                    task.completed ? 'bg-green-50' : 'bg-gray-50'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    {task.completed ? (
                      <CheckCircleIcon className="w-5 h-5 text-green-500" />
                    ) : (
                      <div className="w-5 h-5 rounded-full border-2 border-gray-300" />
                    )}
                    <span className={task.completed ? 'text-gray-500 line-through' : 'text-gray-900'}>
                      {task.title}
                    </span>
                  </div>
                  <div className="flex items-center text-sm text-gray-500">
                    <ClockIcon className="w-4 h-4 mr-1" />
                    {task.duration}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 pt-4 border-t">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">
                  {stats.tasksCompleted} of {stats.tasksToday} tasks completed
                </span>
                <span className="font-medium text-primary-600">
                  {Math.round((stats.tasksCompleted / stats.tasksToday) * 100)}%
                </span>
              </div>
              <div className="mt-2 h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary-500 rounded-full transition-all duration-500"
                  style={{ width: `${(stats.tasksCompleted / stats.tasksToday) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Digital Twin Insights */}
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <SparklesIcon className="w-5 h-5 text-primary-500" />
            <h2 className="text-lg font-semibold text-gray-900">AI Insights</h2>
          </div>

          <div className="space-y-4">
            <div className="p-3 bg-yellow-50 rounded-xl border border-yellow-200">
              <div className="flex items-start space-x-2">
                <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-yellow-800">Attention Needed</p>
                  <p className="text-xs text-yellow-600 mt-1">
                    Your recursion skills need improvement. Practice 5 more problems.
                  </p>
                </div>
              </div>
            </div>

            <div className="p-3 bg-green-50 rounded-xl border border-green-200">
              <div className="flex items-start space-x-2">
                <ArrowTrendingUpIcon className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-green-800">Great Progress!</p>
                  <p className="text-xs text-green-600 mt-1">
                    Your DSA skills improved by 15% this week.
                  </p>
                </div>
              </div>
            </div>

            <div className="p-3 bg-blue-50 rounded-xl border border-blue-200">
              <div className="flex items-start space-x-2">
                <ChartBarIcon className="w-5 h-5 text-blue-600 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-blue-800">Success Prediction</p>
                  <p className="text-xs text-blue-600 mt-1">
                    68% chance of clearing Google Round 1
                  </p>
                </div>
              </div>
            </div>
          </div>

          <Link
            href="/digital-twin"
            className="mt-4 block text-center text-sm text-primary-600 hover:underline"
          >
            View Full Analysis →
          </Link>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
        <div className="space-y-4">
          {recentActivity.map((activity, index) => (
            <div key={index} className="flex items-center justify-between py-3 border-b last:border-0">
              <div className="flex items-center space-x-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  activity.type === 'assessment' ? 'bg-blue-100' :
                  activity.type === 'interview' ? 'bg-orange-100' : 'bg-green-100'
                }`}>
                  {activity.type === 'assessment' && <AcademicCapIcon className="w-5 h-5 text-blue-600" />}
                  {activity.type === 'interview' && <ChatBubbleLeftRightIcon className="w-5 h-5 text-orange-600" />}
                  {activity.type === 'roadmap' && <MapIcon className="w-5 h-5 text-green-600" />}
                </div>
                <div>
                  <p className="font-medium text-gray-900">{activity.title}</p>
                  <p className="text-sm text-gray-500">{activity.time}</p>
                </div>
              </div>
              {activity.score && (
                <span className="text-sm font-medium text-primary-600">{activity.score}</span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
