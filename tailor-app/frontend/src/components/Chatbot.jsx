import React, { useState } from 'react';
import FormattedAnalysis from './FormattedAnalysis.jsx';
import { Send, Loader2 } from 'lucide-react';
import { getBackendUrl } from '../utils/env.js';


const Chatbot = ({ img_urls }) => {
    const API_URL = getBackendUrl();
    const [results, setResults] = useState([]);
    const [messages, setMessages] = useState([]);
    const [prompt, setPrompt] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const ALLOWED_MIME_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];

    // Fetch and validate images before sending to backend
    const fetchAndValidateImage = async (img_url) => {
        const response = await fetch(img_url);
        if (!response.ok) {
            throw new Error(`Failed to fetch image: ${response.statusText}`);
        }
    
        const blob = await response.blob();

        const filename = img_url.split('/').pop(); // Extract filename from URL
        const extension = filename.split('.').pop().toLowerCase();
        let mimeType;

        switch (extension) {
            case 'jpg':
            case 'jpeg':
                mimeType = 'image/jpeg';
                break;
            case 'png':
                mimeType = 'image/png';
                break;
            case 'gif':
                mimeType = 'image/gif';
                break;
            default:
                throw new Error(`Unsupported file extension: ${extension}`);
        }
    
        // Manually set the MIME type
        const file = new File([blob], filename, { type: mimeType });

        return file;
    };
    
    const handleAnalyzeMoodboard = async () => {
        setMessages((prevMessages) => [...prevMessages, { text: "Analyse Moodboard", sender: 'user' }]);
        setIsLoading(true);
    
        try {
            const formData = new FormData();
            for (const img_url of img_urls) {
                const file = await fetchAndValidateImage(img_url);
                formData.append("files", file);
            }
        
            const response = await fetch(`${API_URL}/api/boards/analyze`, {
                method: "POST",
                body: formData,
            });
    
            const data = await response.json();
    
            if (data.success) {
                const result = data.analysis;

                setResults((prevResults) => [...prevResults, result]);
                setMessages((prevMessages) => [...prevMessages, { text: result, sender: 'bot' }]);
            }

        } catch (error) {
            console.error("Error:", error);
            setMessages((prevMessages) => [...prevMessages, { text: `Error: ${error.message}`, sender: 'bot' }]);
            
        } finally {
            setIsLoading(false);
        }
    };
    

    // Handle image analysis
    const handleAnalyzeImages = async () => {
        setMessages((prevMessages) => [...prevMessages, { text: "Analyse Images", sender: 'user' }]);
        setIsLoading(true);

        const analyzeImage = async (img_url) => {
            try {
                const file = await fetchAndValidateImage(img_url);
                const formData = new FormData();
                formData.append("file", file);

                const response = await fetch(`${API_URL}/api/files/analyze`, {
                    method: "POST",
                    body: formData,
                });

                const data = await response.json();
                if (data.success) {
                    const parsedAnalysis = JSON.parse(data.analysis);
                    const result = {
                        image: file,
                        description: parsedAnalysis[0],
                        classification: parsedAnalysis[1],
                        colors: parsedAnalysis[2],
                    };

                    setResults((prevResults) => [...prevResults, result]);
                    setMessages((prevMessages) => [...prevMessages, { text: JSON.stringify(result), sender: 'bot' }]);
                }

            } catch (error) {
                console.error("Error:", error);
                setMessages((prevMessages) => [...prevMessages, { text: `Error: ${error.message}`, sender: 'bot' }]);

            } finally {
                setIsLoading(false);
            }
        };

        await Promise.all(img_urls.map(analyzeImage));
    };

  // "CHATBOT" STUFF"
  const handleSend = () => {
    if (prompt.trim() === '') return;

    setMessages((prevMessages) => [
      ...prevMessages,
      { text: prompt, sender: 'user' },
    ]);
    setPrompt('');
    setIsLoading(true);

    // Simulate bot response after a delay
    setTimeout(() => {
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: 'This is a bot response!', sender: 'bot' },
      ]);
      setIsLoading(false);
    }, 1500);
  };

  return (
    <div className="max-w-lg mx-auto p-4 bg-white shadow-lg rounded-lg">
      {/* Chat Messages Area */}
      <div className="h-80 overflow-y-scroll mb-4 p-4 border border-gray-200 rounded-lg">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'} mb-2`}
          >
            <div
              className={`px-4 py-2 rounded-xl ${
                msg.sender === 'user' ? 'bg-black text-white' : 'bg-gray-200 text-black'
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
      </div>

      {/* Buttons */}
      <button
          onClick={handleAnalyzeImages}
          disabled={isLoading}
          className="p-2 bg-gray-900 rounded-lg hover:bg-gray-700 outline-solid text-white"
      >
        {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Inspector"}
      </button>

      <button
          onClick={handleAnalyzeMoodboard}
          disabled={isLoading}
          className="ml-4 p-2 bg-gray-900 rounded-lg hover:bg-gray-700 outline-solid text-white"
      >
        {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Analyse Moodboard"}
      </button>

      {/* <button
          onClick={handleSend}
          disabled={isLoading}
          className="ml-4 p-2 bg-gray-900 rounded-lg hover:bg-gray-700 outline-solid text-white"
      >
        {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Get Citations"}
      </button> */}

      {/* <div className="flex items-center">
        Text Input // COMMENT OUT
        <input
          type="text"
          placeholder="Type a message"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="w-full py-2 px-4 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-300"
        />
        Send Button // COMMENT OUT
        <button
          onClick={handleSend}
          disabled={isLoading}
          className="ml-2 p-2 bg-gray-900 rounded-lg hover:bg-gray-700 outline-solid"
        >
          {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5 text-white" />}
        </button>
       
      </div> */}
    </div>
  );
}

export default Chatbot;
