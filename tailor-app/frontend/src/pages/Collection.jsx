/* eslint-disable */
import React, { useState, useEffect } from 'react';

// Assets and styling
import '../App.css'
import { getBackendUrl } from '../utils/env.js';

// Components
import Image from '../components/Image';
import UploadModal from '../components/UploadModal';


function MyCollection (){
    const API_URL = getBackendUrl();
    const [uploads, setUploads] = useState([]);
    const [boards, setBoards] = useState([]);
    const userId = '123';
    const [isModalOpen, setIsModalOpen] = useState(false);

    const openModal = () => {
      setIsModalOpen(true);
    };
  
    const closeModal = () => {
      setIsModalOpen(false);
    };

    useEffect(() => {
        if (uploads.length === 0) {
            fetchUploads();
        }
        if (boards.length === 0) {
            fetchMoodboards();
        }
    }, [uploads, boards]);

    async function fetchUploads() {
        const response = await fetch(`${API_URL}/api/files/user/${userId}`);
        const data = await response.json();

        if (data.error) throw new Error(data.error);
        setUploads(data.files);
    }

    async function handleUploadDelete(upload_id) {
        const response = await fetch(`${API_URL}/api/files/${userId}/${upload_id}`,
            { method: 'DELETE',}
        );
        const data = await response.json();

        if (data.error) throw new Error(data.error);
    }

    async function fetchMoodboards() {
        const response = await fetch(`${API_URL}/api/boards/user/${userId}`);
        const data = await response.json();

        if (data.error) throw new Error(data.error);
        setBoards(data.boards);
    }

    async function handleBoardDelete(board_id) {
        const response = await fetch(`${API_URL}/api/boards/${userId}/${board_id}`,
            { method: 'DELETE',}
        );
        const data = await response.json();

        if (data.error) throw new Error(data.error);
    }

    return(
        <div className="flex flex-col justify-center items-center min-h-screen text-white">
        <button className="px-4 py-2 bg-white text-black rounded-full hover:bg-gray-200 flex items-center space-x-2" onClick={openModal}>Upload</button>

            <div className="w-[70%] flex flex-col m-10">
                <div className="flex flex-row justify-between">
                    <h1 className="text-xl">Uploads</h1>
                </div>
                {uploads.map((upload, index) => (
                <div key={uploads[index]} className="col-span-1 row-span-1">
                    <Image
                    className="w-full h-full object-cover"
                        id={upload["_id"]}
                        src={upload["blob_url"]}
                    />
                    {/* TODO: handleUploadDelete(upload["_id"]  Add delete icon besides each uploaded file */}
                </div>
            ))}
            </div>

            <div className="w-[70%] flex flex-col m-10">
                <div className="flex flex-row justify-between">
                    <h1 className="text-xl">Boards</h1>
                </div>
                {boards.map((board, index) => (
                <div key={boards[index]} className="col-span-1 row-span-1">
                    <Image
                    className="w-full h-full object-cover"
                        id={board["_id"]}
                        src={board["blob_url"]}
                    />
                    {/* {/* TODO: handleUploadDelete(board["_id"] Add delete icon besides each board */}
                </div>
            ))}
            </div>
            <UploadModal 
                isOpen={isModalOpen} 
                onClose={closeModal} 
                userId="123" // Replace with actual user ID from auth system
            />
        </div>
    );
}

export default MyCollection;