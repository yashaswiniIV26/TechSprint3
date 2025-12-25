'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  UserCircleIcon,
  DocumentArrowUpIcon,
  AcademicCapIcon,
  BriefcaseIcon,
  StarIcon,
  PencilIcon,
  CheckIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { useStore } from '@/lib/store';
import { profileAPI } from '@/lib/api';
import toast from 'react-hot-toast';

export default function ProfilePage() {
  const { user, profile, setProfile } = useStore();
  const [isEditing, setIsEditing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [editData, setEditData] = useState({
    name: profile?.name || '',
    email: profile?.email || '',
    phone: '',
    college: '',
    branch: '',
    graduation_year: '',
    target_companies: [] as string[],
    target_roles: [] as string[]
  });
  const [newCompany, setNewCompany] = useState('');
  const [newRole, setNewRole] = useState('');
  const [readinessScore, setReadinessScore] = useState<any>(null);

  useEffect(() => {
    if (user) {
      loadProfile();
    }
  }, [user]);

  const loadProfile = async () => {
    try {
      const response = await profileAPI.get(user?.student_id || 'demo_user');
      if (response.data) {
        setProfile(response.data);
        setEditData({
          name: response.data.name || '',
          email: response.data.email || '',
          phone: response.data.phone || '',
          college: response.data.college || '',
          branch: response.data.branch || '',
          graduation_year: response.data.graduation_year?.toString() || '',
          target_companies: response.data.target_companies || [],
          target_roles: response.data.target_roles || []
        });
      }
    } catch (error) {
      console.error('Error loading profile:', error);
    }
  };

  const handleResumeUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.pdf')) {
      toast.error('Please upload a PDF file');
      return;
    }

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('student_id', user?.student_id || 'demo_user');

      const response = await profileAPI.uploadResume(formData);
      toast.success('Resume uploaded and analyzed!');
      await loadProfile();
    } catch (error) {
      toast.error('Failed to upload resume');
      console.error(error);
    } finally {
      setIsUploading(false);
    }
  };

  const calculateReadiness = async () => {
    try {
      const response = await profileAPI.getReadinessScore(user?.student_id || 'demo_user');
      setReadinessScore(response.data);
    } catch (error) {
      toast.error('Failed to calculate readiness score');
      console.error(error);
    }
  };

  const handleSave = async () => {
    try {
      await profileAPI.update(user?.student_id || 'demo_user', editData);
      toast.success('Profile updated!');
      setIsEditing(false);
      await loadProfile();
    } catch (error) {
      toast.error('Failed to update profile');
      console.error(error);
    }
  };

  const addCompany = () => {
    if (newCompany && !editData.target_companies.includes(newCompany)) {
      setEditData(prev => ({
        ...prev,
        target_companies: [...prev.target_companies, newCompany]
      }));
      setNewCompany('');
    }
  };

  const removeCompany = (company: string) => {
    setEditData(prev => ({
      ...prev,
      target_companies: prev.target_companies.filter(c => c !== company)
    }));
  };

  const addRole = () => {
    if (newRole && !editData.target_roles.includes(newRole)) {
      setEditData(prev => ({
        ...prev,
        target_roles: [...prev.target_roles, newRole]
      }));
      setNewRole('');
    }
  };

  const removeRole = (role: string) => {
    setEditData(prev => ({
      ...prev,
      target_roles: prev.target_roles.filter(r => r !== role)
    }));
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Profile</h1>
          <p className="text-gray-500 mt-1">
            Manage your profile and track your placement readiness
          </p>
        </div>
        {!isEditing ? (
          <button
            onClick={() => setIsEditing(true)}
            className="btn-primary flex items-center space-x-2"
          >
            <PencilIcon className="w-5 h-5" />
            <span>Edit Profile</span>
          </button>
        ) : (
          <div className="flex space-x-2">
            <button
              onClick={() => setIsEditing(false)}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button onClick={handleSave} className="btn-primary flex items-center space-x-2">
              <CheckIcon className="w-5 h-5" />
              <span>Save</span>
            </button>
          </div>
        )}
      </div>

      {/* Profile Card */}
      <div className="card">
        <div className="flex items-start space-x-6">
          <div className="relative">
            <div className="w-24 h-24 bg-gradient-to-br from-primary-500 to-accent-500 rounded-full flex items-center justify-center">
              <UserCircleIcon className="w-16 h-16 text-white" />
            </div>
          </div>
          <div className="flex-1">
            {isEditing ? (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                  <input
                    type="text"
                    value={editData.name}
                    onChange={(e) => setEditData(prev => ({ ...prev, name: e.target.value }))}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    value={editData.email}
                    onChange={(e) => setEditData(prev => ({ ...prev, email: e.target.value }))}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                  <input
                    type="tel"
                    value={editData.phone}
                    onChange={(e) => setEditData(prev => ({ ...prev, phone: e.target.value }))}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">College</label>
                  <input
                    type="text"
                    value={editData.college}
                    onChange={(e) => setEditData(prev => ({ ...prev, college: e.target.value }))}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Branch</label>
                  <input
                    type="text"
                    value={editData.branch}
                    onChange={(e) => setEditData(prev => ({ ...prev, branch: e.target.value }))}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Graduation Year</label>
                  <input
                    type="text"
                    value={editData.graduation_year}
                    onChange={(e) => setEditData(prev => ({ ...prev, graduation_year: e.target.value }))}
                    className="input-field"
                  />
                </div>
              </div>
            ) : (
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{profile?.name || 'Student'}</h2>
                <p className="text-gray-500">{profile?.email}</p>
                <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                  <span>{profile?.college || 'Add college'}</span>
                  <span>•</span>
                  <span>{profile?.branch || 'Add branch'}</span>
                  <span>•</span>
                  <span>Class of {profile?.graduation_year || '2025'}</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Resume Upload */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Resume</h3>
        <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center">
          <DocumentArrowUpIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-2">
            {profile?.resume_path ? 'Resume uploaded' : 'Upload your resume'}
          </p>
          <p className="text-sm text-gray-400 mb-4">PDF format, max 5MB</p>
          <label className="btn-primary cursor-pointer inline-block">
            {isUploading ? 'Uploading...' : 'Choose File'}
            <input
              type="file"
              accept=".pdf"
              onChange={handleResumeUpload}
              className="hidden"
              disabled={isUploading}
            />
          </label>
        </div>
      </motion.div>

      {/* Skills Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Skills</h3>
        <div className="space-y-4">
          {profile?.skills && Object.entries(profile.skills).map(([category, skills]) => (
            <div key={category}>
              <h4 className="text-sm font-medium text-gray-700 mb-2 capitalize">{category}</h4>
              <div className="flex flex-wrap gap-2">
                {(skills as string[]).map((skill) => (
                  <span
                    key={skill}
                    className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm"
                  >
                    {skill}
                  </span>
                ))}
                {(skills as string[]).length === 0 && (
                  <span className="text-gray-400 text-sm">No skills added</span>
                )}
              </div>
            </div>
          ))}
          {!profile?.skills && (
            <p className="text-gray-400 text-sm">Upload your resume to extract skills automatically</p>
          )}
        </div>
      </motion.div>

      {/* Target Companies & Roles */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card"
      >
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <BriefcaseIcon className="w-5 h-5 mr-2" />
              Target Companies
            </h3>
            {isEditing && (
              <div className="flex space-x-2 mb-4">
                <input
                  type="text"
                  value={newCompany}
                  onChange={(e) => setNewCompany(e.target.value)}
                  placeholder="Add company"
                  className="input-field flex-1"
                  onKeyPress={(e) => e.key === 'Enter' && addCompany()}
                />
                <button onClick={addCompany} className="btn-primary">Add</button>
              </div>
            )}
            <div className="flex flex-wrap gap-2">
              {editData.target_companies.map((company) => (
                <span
                  key={company}
                  className="px-3 py-1 bg-accent-100 text-accent-700 rounded-full text-sm flex items-center"
                >
                  {company}
                  {isEditing && (
                    <button onClick={() => removeCompany(company)} className="ml-2">
                      <XMarkIcon className="w-4 h-4" />
                    </button>
                  )}
                </span>
              ))}
              {editData.target_companies.length === 0 && (
                <span className="text-gray-400 text-sm">No target companies added</span>
              )}
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <AcademicCapIcon className="w-5 h-5 mr-2" />
              Target Roles
            </h3>
            {isEditing && (
              <div className="flex space-x-2 mb-4">
                <input
                  type="text"
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value)}
                  placeholder="Add role"
                  className="input-field flex-1"
                  onKeyPress={(e) => e.key === 'Enter' && addRole()}
                />
                <button onClick={addRole} className="btn-primary">Add</button>
              </div>
            )}
            <div className="flex flex-wrap gap-2">
              {editData.target_roles.map((role) => (
                <span
                  key={role}
                  className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm flex items-center"
                >
                  {role}
                  {isEditing && (
                    <button onClick={() => removeRole(role)} className="ml-2">
                      <XMarkIcon className="w-4 h-4" />
                    </button>
                  )}
                </span>
              ))}
              {editData.target_roles.length === 0 && (
                <span className="text-gray-400 text-sm">No target roles added</span>
              )}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Placement Readiness Score */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="card bg-gradient-to-r from-primary-600 to-accent-600 text-white"
      >
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold flex items-center">
              <StarIcon className="w-5 h-5 mr-2" />
              Placement Readiness Score
            </h3>
            {readinessScore ? (
              <div className="mt-4">
                <div className="text-5xl font-bold">{readinessScore.overall_score}%</div>
                <p className="text-primary-100 mt-2">{readinessScore.recommendation}</p>
              </div>
            ) : (
              <p className="text-primary-100 mt-2">
                Calculate your readiness based on skills, projects, and assessments
              </p>
            )}
          </div>
          <button
            onClick={calculateReadiness}
            className="bg-white text-primary-600 px-6 py-3 rounded-xl font-semibold hover:bg-primary-50 transition-colors"
          >
            {readinessScore ? 'Recalculate' : 'Calculate Score'}
          </button>
        </div>
        
        {readinessScore && (
          <div className="grid grid-cols-4 gap-4 mt-6 pt-6 border-t border-primary-400">
            <div>
              <div className="text-2xl font-bold">{readinessScore.component_scores?.technical_skills || 0}%</div>
              <div className="text-primary-100 text-sm">Technical</div>
            </div>
            <div>
              <div className="text-2xl font-bold">{readinessScore.component_scores?.projects || 0}%</div>
              <div className="text-primary-100 text-sm">Projects</div>
            </div>
            <div>
              <div className="text-2xl font-bold">{readinessScore.component_scores?.assessments || 0}%</div>
              <div className="text-primary-100 text-sm">Assessments</div>
            </div>
            <div>
              <div className="text-2xl font-bold">{readinessScore.component_scores?.soft_skills || 0}%</div>
              <div className="text-primary-100 text-sm">Soft Skills</div>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}
