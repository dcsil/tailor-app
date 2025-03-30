/* eslint-disable */
import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';

// Assets and styling
import '../App.css'

// Components
import Header from '../components/Header'
import Board from '../components/Board'

function MoodboardPage (){
  const location = useLocation();
  const { prompt, response } = location.state || { prompt: '', response: 'No response received' };
  const { image_ids: img_ids, blob_urls: img_urls } = response;
  
    return (
        <div>
          <Board prompt={prompt} ids={img_ids} urls={img_urls}/>
        </div>
    );
}
export default MoodboardPage
