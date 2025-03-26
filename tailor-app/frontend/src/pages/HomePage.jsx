import React from 'react';

// Assets and styling
import tailorLogo from '../assets/tailor-white-logo.png'
import '../App.css'

// Components
import Header from '../components/Header'
import PromptInput from '../components/PromptInput'
import Footer from '../components/Footer'

function HomePage() {
    return (
      <div className="flex flex-col min-h-screen bg-black text-white">
        <Header/>
        <div className="mb-8">
          <img src={tailorLogo} className="mx-auto" alt="Tailor logo" />
        </div>
        <PromptInput/>
        <Footer/>
      </div>
  )
}

export default HomePage