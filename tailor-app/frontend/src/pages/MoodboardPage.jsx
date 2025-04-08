/* eslint-disable */
import React, { useState, useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'
import { getBackendUrl } from '../utils/env.js'

// Assets and styling
import '../App.css'

// Components
import Header from '../components/Header'
import Board from '../components/Board'
import MoodboardTitle from '../components/MoodboardTitle'

function MoodboardPage() {
  const userId = '123'
  const API_URL = getBackendUrl()
  const location = useLocation()
  const { prompt, response } = location.state || { prompt: '', response: 'No response received' }
  const { image_ids: img_ids, blob_urls: img_urls } = response
  const [title, setTitle] = useState('My Moodboard')

  const firstRender = useRef(true)

  const handleDiscard = async () => {
    // Discard the temporary moodboard from the storage when navigating away from the page to avoid discrepencies
    const response = await fetch(`${API_URL}/api/temp_boards/${userId}/${prompt}`, { method: 'DELETE' })
    const data = await response.json()

    if (data.error) throw new Error(data.error)
  }

  useEffect(() => {
    if (firstRender.current) {
      firstRender.current = false // Skip first render
      return
    }

    return () => {
      handleDiscard()
    }
  }, [])

  return (
    <div>
      {/* Top margin */}
      <div className='py-8'></div>

      {/* Mood board component */}
      <div className='flex flex-col bg-[var(--color-beige)] rounded-md px-3 pb-6'>
        <div>
          <Board prompt={prompt} ids={img_ids} urls={img_urls} />
        </div>
      </div>
    </div>
  )
}
export default MoodboardPage
