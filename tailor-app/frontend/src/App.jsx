
/* eslint-disable */
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';


// Assets and styling
import './App.css'

// Components
import Chat from './components/Chat'
import PromptInput from './components/PromptInput'
import Footer from './components/Footer'
import Moodboard from './components/Moodboard'

//pages
import MoodboardPage from './pages/MoodboardPage'
import MyChat from './pages/Chat'
import HomePage from './pages/HomePage'

// function Home() {
//   return (
//       <div className="flex flex-col min-h-screen bg-black text-white">
//       <div className="mb-8">
//         <img src={tailorLogo} className="mx-auto" alt="Tailor logo" />
//       </div>
//       <PromptInput/>
           
//       {/* <div className="mt-8">
//         <Chat />
//       </div> */}

//       <Footer></Footer>
//     </div>
//   );
// }




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
                <Route path="/" element={<HomePage />} />
                <Route path="/moodboardresult" element={<MoodboardPage />} />
                <Route path="/mychat" element={<MyChat />} />
                <Route path="/moodboard" element={<Moodboard />}/>
            </Routes>

    </Router>
  )
}

export default App