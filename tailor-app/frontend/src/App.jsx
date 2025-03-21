import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Assets and styling
import './App.css'

// Components
import Moodboard from './components/Moodboard'
import HomePage from './pages/HomePage'



function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/moodboard" element={<Moodboard />} />
      </Routes>
    </Router>
  )
}

export default App