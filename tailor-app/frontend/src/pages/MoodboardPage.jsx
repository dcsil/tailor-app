/* eslint-disable */
import React, { useState, useEffect } from 'react';

// Assets and styling
import '../App.css'

// Components
import Header from '../components/Header'
import Board from '../components/Board'

function MoodboardPage (){

    return(
        <div className="flex flex-col min-h-screen text-white">
        <Header/>
        <Board/>
        </div>

    );
}
export default MoodboardPage