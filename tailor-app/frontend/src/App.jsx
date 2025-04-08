/* eslint-disable */
import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'

// Assets and styling
import './App.css'

// Components
import Moodboard from './components/Moodboard'
import Footer from './components/Footer'
import Header from './components/Header'

//pages
import MoodboardPage from './pages/MoodboardPage'
import MyChat from './pages/Chat'
import MyCollection from './pages/Collection'
import HomePage from './pages/HomePage'
import Privacy from './pages/Privacy'
import UploadCollection from './pages/UploadCollection'
import BoardCollection from './pages/BoardCollection'

function App() {
  return (
    <div className='flex flex-col min-h-screen justify-between'>
      <Router>
        <Header />

        <Routes>
          <Route path='/' element={<HomePage />} />
          <Route path='/moodboardresult' element={<MoodboardPage />} />
          <Route path='/mychat' element={<MyChat />} />
          <Route path='/mycollection' element={<MyCollection />} />
          <Route path='/mycollection/uploads' element={<UploadCollection />} />
          <Route path='/mycollection/boards' element={<BoardCollection />} />
          {/* chelsea: /moodboard will be removed */}
          <Route path='/moodboard' element={<Moodboard />} />
          <Route path='/privacy' element={<Privacy />} />
          {/* <Route path="/terms" element={<... />} /> */}
        </Routes>

        <Footer />
      </Router>
    </div>
  )
}

export default App
