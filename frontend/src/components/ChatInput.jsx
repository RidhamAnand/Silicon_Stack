import React, { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';

const ChatInput = ({ onSendMessage, disabled, placeholder }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const message = input.trim();
    if (message && !disabled) {
      onSendMessage(message);
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex items-end gap-2">
        <div className="flex-1 relative">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder || "Message AI Support..."}
            disabled={disabled}
            rows={1}
            className="w-full resize-none bg-gray-50 border border-gray-200 rounded-2xl px-5 py-3.5 pr-12 focus:bg-white focus:ring-2 focus:ring-gray-300 focus:border-transparent outline-none transition-all duration-200 text-[15px] placeholder:text-gray-400"
            style={{
              minHeight: '52px',
              maxHeight: '200px',
            }}
            onInput={(e) => {
              e.target.style.height = 'auto';
              e.target.style.height = Math.min(e.target.scrollHeight, 200) + 'px';
            }}
          />
          <button
            type="submit"
            disabled={disabled || !input.trim()}
            className={`absolute right-2 bottom-2 w-9 h-9 rounded-full flex items-center justify-center transition-all duration-200 ${
              disabled || !input.trim()
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-gray-900 text-white hover:bg-gray-800 hover:scale-105'
            }`}
          >
            {disabled ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>
    </form>
  );
};

export default ChatInput;
