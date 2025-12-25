'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  HomeIcon, 
  UserIcon, 
  AcademicCapIcon, 
  ChartBarIcon,
  MapIcon,
  ChatBubbleLeftRightIcon,
  SparklesIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';
import clsx from 'clsx';

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Profile', href: '/profile', icon: UserIcon },
  { name: 'Assessments', href: '/assessments', icon: AcademicCapIcon },
  { name: 'Skill Gap', href: '/skill-gap', icon: ChartBarIcon },
  { name: 'Roadmap', href: '/roadmap', icon: MapIcon },
  { name: 'Interview Coach', href: '/interview', icon: ChatBubbleLeftRightIcon },
  { name: 'Digital Twin', href: '/digital-twin', icon: SparklesIcon },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="hidden lg:flex lg:flex-shrink-0">
      <div className="flex w-64 flex-col">
        <div className="flex min-h-0 flex-1 flex-col bg-white border-r border-gray-200">
          {/* Logo */}
          <div className="flex h-16 flex-shrink-0 items-center px-4 border-b border-gray-200">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center">
                <SparklesIcon className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold gradient-text">Velionx</span>
            </Link>
          </div>

          {/* Navigation */}
          <div className="flex flex-1 flex-col overflow-y-auto pt-5 pb-4">
            <nav className="flex-1 space-y-1 px-3">
              {navigation.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={clsx(
                      'group flex items-center px-3 py-3 text-sm font-medium rounded-xl transition-all duration-200',
                      isActive
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    )}
                  >
                    <item.icon
                      className={clsx(
                        'mr-3 h-5 w-5 flex-shrink-0 transition-colors',
                        isActive
                          ? 'text-primary-600'
                          : 'text-gray-400 group-hover:text-gray-500'
                      )}
                    />
                    {item.name}
                    {isActive && (
                      <div className="ml-auto w-1.5 h-1.5 rounded-full bg-primary-500" />
                    )}
                  </Link>
                );
              })}
            </nav>
          </div>

          {/* Settings */}
          <div className="flex-shrink-0 border-t border-gray-200 p-4">
            <Link
              href="/settings"
              className="group flex items-center px-3 py-3 text-sm font-medium text-gray-600 rounded-xl hover:bg-gray-50 hover:text-gray-900 transition-all duration-200"
            >
              <Cog6ToothIcon className="mr-3 h-5 w-5 text-gray-400 group-hover:text-gray-500" />
              Settings
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
