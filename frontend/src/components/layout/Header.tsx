import React from 'react';
import { BellIcon, UserCircleIcon } from '@heroicons/react/24/outline';

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="flex items-center justify-between h-16 px-6">
        <div className="flex items-center">
          <h2 className="text-lg font-semibold text-gray-900">StockTracker Pro</h2>
        </div>
        
        <div className="flex items-center space-x-4">
          <button className="p-2 text-gray-400 hover:text-gray-500">
            <BellIcon className="h-6 w-6" />
          </button>
          <button className="p-2 text-gray-400 hover:text-gray-500">
            <UserCircleIcon className="h-6 w-6" />
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
