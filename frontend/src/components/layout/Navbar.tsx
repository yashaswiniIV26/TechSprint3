'use client';

import { useState } from 'react';
import { 
  BellIcon, 
  MagnifyingGlassIcon,
  Bars3Icon 
} from '@heroicons/react/24/outline';
import { useStore } from '@/lib/store';

export default function Navbar() {
  const [searchQuery, setSearchQuery] = useState('');
  const { user } = useStore();

  return (
    <header className="bg-white border-b border-gray-200 flex-shrink-0">
      <div className="flex h-16 items-center justify-between px-6">
        {/* Mobile menu button */}
        <button className="lg:hidden p-2 rounded-lg hover:bg-gray-100">
          <Bars3Icon className="h-6 w-6 text-gray-500" />
        </button>

        {/* Search */}
        <div className="flex-1 max-w-lg mx-4">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search for skills, companies, resources..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
            />
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <button className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors">
            <BellIcon className="h-6 w-6 text-gray-500" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
          </button>

          {/* User profile */}
          <div className="flex items-center space-x-3">
            <div className="hidden sm:block text-right">
              <p className="text-sm font-medium text-gray-900">
                {user?.name || 'Student'}
              </p>
              <p className="text-xs text-gray-500">
                Readiness: {user?.readiness_score || 0}%
              </p>
            </div>
            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-white font-semibold">
              {user?.name?.charAt(0) || 'S'}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
