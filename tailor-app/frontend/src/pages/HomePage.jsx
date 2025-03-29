import React from 'react';

// Assets and styling
import tailorLogo from '../assets/tailor-white-logo.png'
import '../App.css'

// Components
import PromptInput from '../components/PromptInput'

function HomePage() {
    return (
      <div>
        <div className="mb-8">
          <img src={tailorLogo} className="mx-auto" alt="Tailor logo" />
        </div>
        <PromptInput/>
      </div>
  )
}

export default HomePage