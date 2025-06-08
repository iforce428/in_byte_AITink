import React, { useState } from 'react';
import { Send, MessageCircle, Bot, User } from 'lucide-react';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

export const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello! I can help you analyze alumni data. Ask me questions about graduation trends, programs, job placements, or geographic distribution.',
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // In a real implementation, you would send a POST request to server.py
      /*
      const response = await fetch('/api/chatbot', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: inputValue,
          context: 'alumni_dashboard'
        }),
      });
      
      const data = await response.json();
      */

      // Mock response for demonstration
      await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate API delay
      
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: generateMockResponse(inputValue),
        sender: 'bot',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botResponse]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error processing your request. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const generateMockResponse = (query: string): string => {
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes('graduation') || lowerQuery.includes('trend')) {
      return 'Based on the graduation trend data, we see steady growth in alumni numbers from 2018 to 2023, with a peak of 423 graduates in 2023. The 2024 numbers are partial as the year is still ongoing.';
    } else if (lowerQuery.includes('gender') || lowerQuery.includes('diversity')) {
      return 'Our alumni network shows good gender diversity with 52% female and 42% male graduates. We also have 89 non-binary alumni and 45 who prefer not to specify, demonstrating our inclusive environment.';
    } else if (lowerQuery.includes('program') || lowerQuery.includes('popular')) {
      return 'Computer Science is our most popular program with 567 alumni, followed by Business Administration (423) and Engineering (389). These three programs account for about 60% of our alumni base.';
    } else if (lowerQuery.includes('job') || lowerQuery.includes('career')) {
      return 'Software Engineer is the most common career path for our alumni (234), followed by Product Manager (167) and Data Analyst (143). This reflects the strong tech focus of our programs.';
    } else if (lowerQuery.includes('location') || lowerQuery.includes('country') || lowerQuery.includes('geographic')) {
      return 'Our alumni are globally distributed, with the highest concentration in the United States (678), followed by Canada (234) and the United Kingdom (189). This international presence opens great networking opportunities.';
    } else {
      return 'I can help you analyze various aspects of our alumni data including graduation trends, gender distribution, program popularity, career paths, and geographic spread. What specific information would you like to know?';
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-4">
        <div className="flex items-center space-x-3">
          <div className="bg-white/20 rounded-full p-2">
            <MessageCircle className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-white font-semibold">Alumni Insights Chatbot</h3>
            <p className="text-blue-100 text-sm">Ask questions about alumni data</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="h-80 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex items-start space-x-3 ${
              message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
            }`}
          >
            <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
              message.sender === 'user' 
                ? 'bg-blue-600 text-white' 
                : 'bg-purple-100 text-purple-600'
            }`}>
              {message.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>
            <div className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${
              message.sender === 'user'
                ? 'bg-blue-600 text-white ml-auto'
                : 'bg-gray-100 text-gray-800'
            }`}>
              <p className="text-sm leading-relaxed">{message.text}</p>
              <p className={`text-xs mt-2 ${
                message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
              }`}>
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center">
              <Bot className="w-4 h-4" />
            </div>
            <div className="bg-gray-100 rounded-2xl px-4 py-3">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-gray-100 p-4">
        <div className="flex space-x-3">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about alumni trends, programs, careers..."
            className="flex-1 border border-gray-300 rounded-xl px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={!inputValue.trim() || isLoading}
            className="bg-blue-600 text-white rounded-xl px-4 py-2 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};