import React, { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { getBackendUrl } from '../utils/env.js';


const Chatbot = ({ img_urls }) => {
    // Backend
    const API_URL = getBackendUrl();
    const [results, setResults] = useState([]);

    // "Chatbot" stuff
    const [messages, setMessages] = useState([]);
    const [prompt, setPrompt] = useState('');
    const [isLoading, setIsLoading] = useState(false);
  
    // Handle image analysis
    const handleAnalyzeMoodboard = async () => {
        setPrompt("Analyse Moodboard");
        setMessages((prevMessages) => [
            ...prevMessages,
            { text: prompt, sender: 'user' },
          ]);
          setPrompt('');
          setIsLoading(true);

        try {
            const formData = new FormData();

            console.log(img_urls)

            for (const img_url of img_urls) {
                const blobResponse = await fetch(img_url);
                if (!blobResponse.ok) {
                    throw new Error(`Failed to fetch file from Azure: ${blobResponse.statusText}`);
                }

                const blob = await blobResponse.blob();
                const file = new File([blob], "moodboard-img.jpg", { type: blob.type });

            
                formData.append("files", file);
            }

            const response = await fetch(`${API_URL}/api/boards/analyze`, {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                const result = JSON.parse(data.analysis);

                // Update state with new results (spread old ones)
                setResults((prevResults) => [...prevResults, result]);

                setMessages((prevMessages) => [
                    ...prevMessages,
                    { text: result, sender: 'bot' },
                ]);
            }
        } catch (error) {
            console.error("Error:", error);
        } finally {
            setIsLoading(false);
        }
    };

    // Handle image analysis
    const handleAnalyzeImages = async () => {
        setPrompt("Analyse Images");
        setMessages((prevMessages) => [
            ...prevMessages,
            { text: prompt, sender: 'user' },
          ]);
          setPrompt('');
          setIsLoading(true);

        const analyzeImage = async (img_url) => {
            try {
                const blobResponse = await fetch(img_url);
                if (!blobResponse.ok) {
                    throw new Error(`Failed to fetch file from Azure: ${blobResponse.statusText}`);
                }

                const blob = await blobResponse.blob();
                const file = new File([blob], "single-img.jpg", { type: blob.type });

                const formData = new FormData();
                formData.append("file", file);

                const response = await fetch(`${API_URL}/api/files/analyze`, {
                    method: "POST",
                    body: formData
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
                    console.log(result);

                    // Update state with new results (spread old ones)
                    setResults((prevResults) => [...prevResults, result]);

                    setMessages((prevMessages) => [
                        ...prevMessages,
                        { text: result, sender: 'bot' },
                    ]);
                }
            } catch (error) {
                console.error("Error:", error);
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
        {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Analyse Images"}
      </button>

      <button
          onClick={handleAnalyzeMoodboard}
          disabled={isLoading}
          className="ml-4 p-2 bg-gray-900 rounded-lg hover:bg-gray-700 outline-solid text-white"
      >
        {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Analyse Moodboard"}
      </button>

      <button
          onClick={handleSend}
          disabled={isLoading}
          className="ml-4 p-2 bg-gray-900 rounded-lg hover:bg-gray-700 outline-solid text-white"
      >
        {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Get Citations"}
      </button>

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
