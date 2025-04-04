import { useState } from "react";
import { getBackendUrl } from '../utils/env.js';
import { Search, Paperclip, Send, Scissors, Loader2 } from 'lucide-react';

import ChatbotUI from "./Chatbot.jsx";

const AnalyzeImages = ( {img_urls }) => {
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState([]);
    const API_URL = getBackendUrl();

    const handleChatInput = async () => {
        setLoading(true);
    
        const processImage = async (img_url) => {
            try {
                const blobResponse = await fetch(img_url);
                if (!blobResponse.ok) {
                    throw new Error(`Failed to fetch file from Azure: ${blobResponse.statusText}`);
                }
    
                const blob = await blobResponse.blob();
                const file = new File([blob], "uploaded-file.jpg", { type: blob.type });
    
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
                        description: parsedAnalysis[0],
                        classification: parsedAnalysis[1],
                        colors: parsedAnalysis[2],
                    };
    
                    // Update state with new results (spread old ones)
                    setResults((prevResults) => [...prevResults, result]);
                }
            } catch (error) {
                console.error("Error:", error);
            } finally {
                setLoading(false);
            }
        };
    
        // Process all images simultaneously
        await Promise.all(img_urls.map(processImage));
    };

    return (
        <div className="bg-white">
        <button onClick={handleChatInput}
                className="gap-4 px-3 py-1.5 rounded-xl border-gray-600 border-2 bg-white cursor-pointer"
                disabled={loading}
        >
            Analyse Images
        </button>

        <div className="text-left">
            {results.map((result, index) => (
                <div key={index} className="result-card">
                    <p>Image #{index + 1}:</p>
                    <p><strong>Description:</strong> {result.description}</p>
                    <p><strong>Classification:</strong> {result.classification}</p>
                    <p><strong>Colors:</strong> {result.colors}</p>
                </div>
            ))}
        </div>
        </div>
    );
}

export default AnalyzeImages;
