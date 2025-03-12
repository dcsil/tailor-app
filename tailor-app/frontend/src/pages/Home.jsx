import React from 'react';
import { useNavigate } from "react-router-dom";
import tailorLogo from '../assets/tailor-blank-bg.png'
import '../App.css'
import Chat from '../components/Chat'

const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen">
      <div className="mb-8">
        <img src={tailorLogo} className="h-16 mx-auto" alt="Tailor logo" />
      </div>
      <div className="mt-8">
        <Chat />
      </div>
      <a onClick={() => navigate("/privacy")} title="privacy">Privacy</a>
    </div>
  );
}

export default Home;
