import React, { useState } from 'react';
import FormattedAnalysis from './FormattedAnalysis.jsx';
import { Send, Loader2 } from 'lucide-react';
import { getBackendUrl } from '../utils/env.js';


const MoodboardAnalysisTab = ({ img_urls, setIsLoading }) => {
    const API_URL = getBackendUrl();
    const [analysis, setAnalysis] = useState("");
    const [error, setError] = useState("");

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

                setAnalysis(result);
            }

        } catch (e) {
            console.error("Error:", e);
            setError(e);
            
        } finally {
            setIsLoading(false);
        }
    };

  return (
    <div>
        { !analysis ? handleAnalyzeMoodboard() : error }

        <FormattedAnalysis analysis={analysis} />
    </div>
  );
}

export default MoodboardAnalysisTab;
