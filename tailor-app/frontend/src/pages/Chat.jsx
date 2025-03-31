/* eslint-disable */
import React, { useState, useEffect } from 'react';
import { useLocation } from "react-router-dom";

// Assets and styling
import '../App.css'
import { getBackendUrl } from '../utils/env.js';

// Components
import ChatHistoryList from '../components/ChatHistoryList'

function MyChat (){
    const API_URL = getBackendUrl();
    const location = useLocation();
    const [chatHistory, setChatHistory] = useState([]);

    async function fetchChatHistory() {
        const response = await fetch(`${API_URL}/api/history`);
        const data = await response.json();

        if (data.error) throw new Error(data.error);
        setChatHistory(data);
    }

    if (location.state?.fetchData && chatHistory.length === 0) {
        fetchChatHistory();
    }

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