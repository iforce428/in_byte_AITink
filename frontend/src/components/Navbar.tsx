import React from 'react';
import { LayoutDashboard } from 'lucide-react';
import asbLogo from '../assets/images/Asia-School-of-Business-ASB-Logo.png';

export const Navbar: React.FC = () => {
  return (
    <nav className="bg-white border-b border-gray-100 fixed w-full top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <a 
              href="https://asbhive.edu.my/" 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex items-center space-x-2"
            >
              <img 
                src={asbLogo}
                alt="ASBhive Logo" 
                className="h-8 w-auto"
              />
              <span className="text-gray-800 font-semibold">ASBhive</span>
            </a>
          </div>
          
          <div className="flex items-center">
            <a 
              href="/dashboard" 
              className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 transition-colors"
            >
              <LayoutDashboard className="w-5 h-5" />
              <span>Dashboard</span>
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
}; 