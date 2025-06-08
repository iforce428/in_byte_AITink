import React from 'react';
import { Dashboard } from './components/Dashboard';
import { Chatbot } from './components/Chatbot';

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        {/* Dashboard */}
        <Dashboard />
        
        {/* Chatbot Section */}
        <div className="mt-12">
          <div className="max-w-4xl mx-auto">
            <Chatbot />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;