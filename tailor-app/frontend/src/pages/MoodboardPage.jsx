/* eslint-disable */
import React, { useState, useEffect } from 'react';

// Assets and styling
import '../App.css'

// Components
import Header from '../components/Header'
import Board from '../components/Board'
import BoardTest from '../components/BoardTest'

function MoodboardPage (){

    return(
        <div className="flex flex-col min-h-screen bg-black text-white">
        <Header/>
        <BoardTest/>
        </div>

    );
}
export default MoodboardPage