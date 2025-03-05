import React, { useState, useEffect } from 'react';
import tailorLogo from './assets/tailor-blank-bg.png'
import './App.css'
import Chat from './components/Chat'
import { getBackendUrl } from './utils/env';

function App() {
  const [count, setCount] = useState(0)
  
  // temporary for checking backend and frontend integration
  const [healthStatus, setHealthStatus] = useState(null);
  const API_URL = getBackendUrl();
  
  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then(response => response.json()) 
      .then(data => {
        setHealthStatus(data.status); 
      })
      .catch(error => {
        console.error("Error fetching health check:", error); 
      });
  }, []);
  
  return (
    <div className="min-h-screen">
      <div className="mb-8">
        <img src={tailorLogo} className="h-16 mx-auto" alt="Tailor logo" />
      </div>
      <h1>Hello World!</h1>

      <button onClick={() => {throw new Error("This is your first error!");}}>Break the world</button>
      
      <div className="mt-8">
        <Chat />
      </div>
      <p className="read-the-docs">
        {healthStatus ? ` - Backend Status: ${healthStatus}` : " - Checking backend connection"}
      </p>
    </div>
  )
}

export default App