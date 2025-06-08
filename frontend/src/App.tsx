import React from 'react';
import { Dashboard } from './components/Dashboard';
import { Chatbot } from './components/Chatbot';
import { Navbar } from './components/Navbar';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="pt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Dashboard />
        </div>
      </main>
      <Chatbot />
    </div>
  );
}

export default App;