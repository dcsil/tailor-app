/* eslint-disable */
import React, { useState, useEffect } from 'react';

// Assets and styling
import '../App.css'

// Components
import ChatHistoryList from '../components/ChatHistoryList'

function MyChat (){

    const chatHistory = [
        { id: 1, title: "Dark Academia Aesthetic", date: "2/11/2025"},
        { id: 2, title: "Vintage Fashion", date: "3/13/2025"},
      ];

    return(
        <div className="flex flex-col justify-center items-center min-h-screen text-white">
            <div className="w-[70%] flex flex-col m-10">
                <div className="flex flex-row justify-between">
                    <h1 className="text-xl">Prompt History</h1>
                    <h2 className="text-l">Date</h2>
                </div>
                <ChatHistoryList chatHistory={chatHistory} />
            </div>
        </div>
    );
}
export default MyChat