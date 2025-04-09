/* eslint-disable */
import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

// Assets and styling
import '../App.css'
import { getBackendUrl } from '../utils/env.js'

// Components
import UploadModal from '../components/UploadModal'
import CollectionItem from '../components/CollectionItem.jsx'

function MyCollection() {
  const API_URL = getBackendUrl()
  const navigate = useNavigate()
  const [uploads, setUploads] = useState(null)
  const [boards, setBoards] = useState(null)
  const userId = '123'
  const [isModalOpen, setIsModalOpen] = useState(false)

  const openModal = () => {
    setIsModalOpen(true)
  }

  const closeModal = () => {
    setIsModalOpen(false)
  }

  async function fetchUploads() {
    const response = await fetch(`${API_URL}/api/files/user/${userId}`)
    const data = await response.json()

    if (data.error) throw new Error(data.error)
    setUploads(data.files)
  }

  async function fetchMoodboards() {
    const response = await fetch(`${API_URL}/api/boards/user/${userId}`)
    const data = await response.json()

    if (data.error) throw new Error(data.error)
    setBoards(data.boards)
  }

  useEffect(() => {
    if (uploads === null) {
      fetchUploads()
    }
  }, [uploads])

  useEffect(() => {
    if (boards === null) {
      fetchMoodboards()
    }
  }, [boards])

  return (
    <div className='flex flex-col min-h-screen text-white p-4'>
      <div className='flex justify-center w-full py-8'>
        <button
          className='px-6 py-3 bg-white text-black rounded-full hover:bg-gray-200 flex items-center space-x-2 transition-colors duration-200 font-medium hover:cursor-pointer'
          onClick={openModal}
          data-tip="Upload a new image"
        >
          <span>Upload</span>
        </button>
        <ReactTooltip place="top" type="dark" effect="solid" />
      </div>

      <div className='w-[50%]'>
        <div className='grid grid-cols-2 gap-4 justify-start'>
          <CollectionItem title='Uploads' files={uploads} image={uploads?.[0]?.blob_url} count={uploads?.length} />
          <CollectionItem title='Moodboards' files={boards} image={boards?.[0]?.blob_url} count={boards?.length} />
        </div>
      </div>

      <UploadModal isOpen={isModalOpen} onClose={closeModal} userId='123' />
    </div>
  )
}

export default MyCollection
