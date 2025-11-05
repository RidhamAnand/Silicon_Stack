import React from 'react';
import { Sparkles } from 'lucide-react';

const TypingIndicator = () => {
  return (
    <div className="flex justify-start mb-6 animate-fade-in">
      <div className="flex items-center gap-3">
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-gray-800 to-gray-900 flex items-center justify-center">
          <Sparkles className="w-4 h-4 text-white" />
        </div>

        <div className="bg-gray-50 border border-gray-100 rounded-2xl px-5 py-3">
          <div className="flex gap-1.5">
            <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;
