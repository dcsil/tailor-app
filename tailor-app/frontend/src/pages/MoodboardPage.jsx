/* eslint-disable */
import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';

// Assets and styling
import '../App.css'

// Components
import Header from '../components/Header'
import Board from '../components/Board'
import MoodboardTitle from '../components/MoodboardTitle'

function MoodboardPage (){
  const location = useLocation();
  const { prompt, response } = location.state || { prompt: '', response: 'No response received' };
  const { image_ids: img_ids, blob_urls: img_urls } = response;
  
    return (
        <div>
          {/* Top margin */}
          <div className="py-8">
          </div>

          {/* Mood board component */}
          <div className="flex flex-col bg-[var(--color-beige)] rounded-md px-3 pb-6">
            
              <MoodboardTitle/>
            <div>
              <Board prompt={prompt} ids={img_ids} urls={img_urls}/>
            </div>
          </div>

        </div>
    );
}
export default MoodboardPage
