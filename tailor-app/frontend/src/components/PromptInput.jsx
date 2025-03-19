import React, { useState, useEffect } from 'react';
import { Search, Paperclip, Send, Scissors } from 'lucide-react';

const PromptInput = () => {
  const [prompt, setPrompt] = useState('');

  return (
    <div className="w-full">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="How can I inspire you?"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="w-full py-4 px-12 rounded-2xl bg-white text-black placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-300"
            />
          </div>
          
          {/* Action Buttons */}
          <div className="flex justify-end mt-4 space-x-2">
            <button className="px-4 py-2 bg-white text-black rounded-full hover:bg-gray-100 transition-colors flex items-center space-x-2">
              <Paperclip className="w-5 h-5" />
              <span>Attach</span>
            </button>
            <button className="p-2 bg-gray-900 rounded-full hover:bg-gray-800 transition-colors">
              <Send className="w-5 h-5 text-white" />
            </button>
          </div>
        </div>
  );
};

export default PromptInput;