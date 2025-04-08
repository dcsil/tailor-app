import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

const Moodboard = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const { prompt, response } = location.state || { prompt: '', response: 'No response received' }

  return (
    <div className='p-6 text-gray-300'>
      <h2 className='text-xl font-semibold'>Chat Response</h2>
      <p className='mt-2'>
        <strong>You:</strong> {prompt}
      </p>
      <p className='mt-2'>
        <strong>Charlie:</strong> {response}
      </p>
      <button onClick={() => navigate('/')} className='mt-4 px-4 py-2 bg-gray-900 rounded-full hover:bg-gray-800 outline-solid'>
        Go Back
      </button>
    </div>
  )
}

export default Moodboard
