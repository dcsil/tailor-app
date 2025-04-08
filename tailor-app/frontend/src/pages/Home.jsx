import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import tailorLogo from '../assets/tailor-blank-bg.png'
import '../App.css'
import Chat from '../components/Chat'
import UploadModal from '../components/UploadModal'

const Home = () => {
  const navigate = useNavigate()
  const [isModalOpen, setIsModalOpen] = useState(false)

  const openModal = () => {
    setIsModalOpen(true)
  }

  const closeModal = () => {
    setIsModalOpen(false)
  }

  return (
    <div className='min-h-screen'>
      <div className='mb-8'>
        <img src={tailorLogo} className='h-16 mx-auto' alt='Tailor logo' />
      </div>

      {/* Upload button */}
      <div className='flex justify-center mb-4'>
        <button onClick={openModal} className='px-4 py-2 bg-blue-500 text-white rounded'>
          Upload Image
        </button>
      </div>

      <div className='mt-8'>
        <Chat />
      </div>
      <a onClick={() => navigate('/privacy')} title='privacy'>
        Privacy
      </a>

      {/* Upload Modal */}
      <UploadModal
        isOpen={isModalOpen}
        onClose={closeModal}
        userId='123' // Replace with actual user ID from auth system
      />
    </div>
  )
}

export default Home
