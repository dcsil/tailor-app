
/* eslint-disable */
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';


// Assets and styling
import './App.css'

// Components

import Chat from './components/Chat'
import PromptInput from './components/PromptInput'
import Footer from './components/Footer'
import Moodboard from './pages/Moodboard'
import MyChat from './pages/Chat'

function Home() {
  return (
      <div className="flex flex-col min-h-screen bg-black text-white">
      <div className="mb-8">
        <img src={tailorLogo} className="mx-auto" alt="Tailor logo" />
      </div>
      <PromptInput/>
           
      {/* <div className="mt-8">
        <Chat />
      </div> */}

      <Footer></Footer>
    </div>
  );
}




function App() {
  return (

    // <div className="flex flex-col min-h-screen bg-black text-white">
    //   <div className="mb-8">
    //     <img src={tailorLogo} className="mx-auto" alt="Tailor logo" />
    //   </div>
    //   <PromptInput/>
           
    //   {/* <div className="mt-8">
    //     <Chat />
    //   </div> */}

    //   <Footer></Footer>
      
    // </div>
    <Router>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/moodboard" element={<Moodboard />} />
                <Route path="/mychat" element={<MyChat />} />
            </Routes>

    </Router>
  )
}

export default App