
/* eslint-disable */
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';


// Assets and styling
import './App.css'

// Components
import Moodboard from './pages/Moodboard'
import HomePage from './pages/HomePage'
import MyChat from './pages/Chat'

function App() {
  return (
    <Router>
            <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/moodboard" element={<Moodboard />} />
                <Route path="/mychat" element={<MyChat />} />
            </Routes>

    </Router>
  )
}

export default App