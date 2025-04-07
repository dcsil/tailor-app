import React, { useState, useEffect } from 'react';
import FormattedAnalysis from './FormattedAnalysis.jsx';
import { Loader2 } from 'lucide-react';
import { getBackendUrl } from '../utils/env.js';
import ImageInspector from './ImageInspector.jsx';

const MoodboardTabs = ({ img_urls, img_ids, prompt, properties }) => {
  const API_URL = getBackendUrl();
  const [analysis, setAnalysis] = useState("");
  const [reanalyse, setReanalyse] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [descriptions, setDescriptions] = useState({}); // dict of image id : description
  const user_id = '123';

  useEffect(() => {
    const fetchDescriptions = async () => {
      const descriptionsDict = {};

      for (let i = 0; i < img_ids.length; i++) {
        const file_id = img_ids[i];

        try {
          const response = await fetch(`${API_URL}/api/files/${user_id}/${file_id}`);

          if (response.ok) {
            const data = await response.json();

            if (data.success) {
              descriptionsDict[file_id] = data.file_data.description || "";
            }
          } 

        } catch (error) {
          console.error(`Error fetching description for file_id ${file_id}:`, error);
          descriptionsDict[file_id] = "";
        }
      }
      
      setDescriptions(descriptionsDict);
    };

    if (img_ids && img_ids.length > 0) {
        fetchDescriptions();
      }
    }, [img_ids, user_id, API_URL]);

  const Tab = {
    INSPECTOR: "inspector",
    ANALYSIS: "analysis",
  };
  const [tab, setTab] = useState(Tab.INSPECTOR);

  const resizeMoodboardImage = (img, maxWidth, maxHeight) => {
    let width = img.width;
    let height = img.height;

    // Maintain aspect ratio
    const aspectRatio = width / height;
    if (width > maxWidth || height > maxHeight) {
      if (width > height) {
        width = maxWidth;
        height = width / aspectRatio;
      } else {
        height = maxHeight;
        width = height * aspectRatio;
      }
    }

    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0, width, height);
    return canvas;
  };

  const combineImages = async (imageUrls, maxWidth = 170, maxHeight = 300) => {
    const images = await Promise.all(
      imageUrls.map(async (url) => {
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`Failed to fetch image: ${url}`);
        }
        const blob = await response.blob();
        const img = await createImageBitmap(blob);
        return resizeMoodboardImage(img, maxWidth, maxHeight); // Resize each image
      })
    );

    // Calculate the dimensions for the combined image
    const totalWidth = Math.max(...images.map((img) => img.width));
    const totalHeight = images.reduce((sum, img) => sum + img.height, 0);

    // Create a canvas to draw the combined image
    const canvas = document.createElement("canvas");
    canvas.width = totalWidth;
    canvas.height = totalHeight;
    const ctx = canvas.getContext("2d");

    let yOffset = 0;
    for (const img of images) {
      ctx.drawImage(img, 0, yOffset);
      yOffset += img.height;
    }

    // Convert the canvas to a Blob with compression
    return new Promise((resolve) => {
      canvas.toBlob((blob) => {
        resolve(blob);
      }, "image/png", 0.8); // Compress the image (quality: 0.8)
    });
  };
  
  const handleAnalyzeMoodboard = async () => {
    setIsLoading(true);

    try {
      // Combine all images into a single image
      const combinedImageBlob = await combineImages(img_urls);
      if (!combinedImageBlob) {
        throw new Error("Failed to combine images");
      }

      // Convert descriptions dict to list
      const descriptionsList = img_ids.map(file_id => descriptions[file_id] || "");
      

      const formData = new FormData();
      formData.append("file", combinedImageBlob, "combined_moodboard.png");
      formData.append("image_descriptions", JSON.stringify(descriptionsList));

      const response = await fetch(`${API_URL}/api/boards/analyze`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setAnalysis(data.analysis);
        console.log(analysis)
      } else {
        throw new Error(data.message || "Failed to analyze moodboard");
      }
    } catch (error) {
      console.error("Error analyzing moodboard:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleMoodboardAnalysisTab = async () => {
    setTab(Tab.ANALYSIS);

    if (analysis) return;
    await handleAnalyzeMoodboard();
  };

  const reanalyseMoodboard = async () => {
    setAnalysis("");
    await handleAnalyzeMoodboard();
  }

  return (
    <div className="h-[80vh] ml-2 p-4 bg-white border-2 border-gray-300 rounded overflow-hidden max-h-[80vh] w-full mr-4">
      {/* Tab Headers */}
      <div className="flex border-b border-gray-300">
        <button
          onClick={() => setTab(Tab.INSPECTOR)}
          className={`flex-1 py-2 px-4 text-center text-sm font-medium ${
            tab === Tab.INSPECTOR ? 'bg-black text-gray-100' : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Inspector
        </button>
        <button
          onClick={handleMoodboardAnalysisTab}
          className={`flex-1 py-2 px-4 text-center text-sm font-medium ${
            tab === Tab.ANALYSIS ? 'bg-black text-gray-100' : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Moodboard Analysis
        </button>
      </div>

      {/* Panel */}
      <div
        className="relative overflow-y-scroll border border-gray-200 rounded p-4 mt-4"
        style={{ height: 'calc(87%)' }}
      >
        {/* Overlay Loader */}
        {isLoading && (
          <div className="absolute inset-0 flex justify-center items-center">
            <Loader2 className="w-10 h-10 animate-spin" />
          </div>
        )}

        {tab === Tab.ANALYSIS ? 
          <div>
            <FormattedAnalysis analysis={analysis} />
            {!isLoading && 
              <button 
                onClick={reanalyseMoodboard}
                className="px-4 py-2 bg-black text-white rounded-full hover:bg-gray-600"
              >
                Reanalyse
              </button>
            }
          </div> 
          : <ImageInspector urls={img_urls} properties={properties}/>}
      </div>
    </div>
  );
};

export default MoodboardTabs;
