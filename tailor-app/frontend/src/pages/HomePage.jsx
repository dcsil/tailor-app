import React from 'react';

// Assets and styling
import tailorLogo from '../assets/tailor-white-logo.png'
import '../App.css'

// Components
import PromptInput from '../components/PromptInput'
import Footer from '../components/Footer'
import Header from '../components/Header'

function HomePage() {
    return (
      <div className="flex flex-col items-center min-h-screen text-white">
        <Header/>
        <div className="mb-16 mt-20 masking-container">
          <h1 className="masked-text">TAILOR</h1>
          {/* <img src={tailorLogo} className="mx-auto" alt="Tailor logo" /> */}
        </div>
        <PromptInput/>
        <Footer/>
      </div>
  )
}

export default HomePage