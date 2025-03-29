/* eslint-disable */
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';


// Assets and styling
import './App.css'

// Components
import Moodboard from './components/Moodboard'

//pages
import MoodboardPage from './pages/MoodboardPage'
import MyChat from './pages/Chat'
import HomePage from './pages/HomePage'
import Privacy from "./pages/Privacy"


function App() {
  return (
    <Router>
            <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/moodboardresult" element={<MoodboardPage />} />
                <Route path="/mychat" element={<MyChat />} />
                <Route path="/moodboard" element={<Moodboard />}/>
                <Route path="/privacy" element={<Privacy />} />
            </Routes>

    </Router>
  )
}

export default App;