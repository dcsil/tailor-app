/* eslint-disable */
import React, { useState, useRef, useEffect } from 'react'
import { getBackendUrl } from '../utils/env.js'

import ColourPalette from './ColourPalette.jsx'

const ImageInspector = ({ urls, properties }) => {
  const API_URL = getBackendUrl()
  const [description, setDescription] = useState('')
  const id = properties?.get('id')
  const user_id = '123'

  useEffect(() => {
    if (!id) return

    const fetchDescription = async () => {
      try {
        const response = await fetch(`${API_URL}/api/files/${user_id}/${id}`)
        if (response.ok) {
          const data = await response.json()
          if (data.success) {
            setDescription(data.file_data.description)
          }
        } else {
          console.error('Failed to fetch description')
        }
      } catch (error) {
        console.error(`Error fetching description for ID ${id}:`, error)
      }
    }

    fetchDescription()
  }, [id])

  return (
    <div className='max-h-[80vh] rounded w-full bg-white'>
      <p className='mb-2 font-bold'>Image Properties</p>
      <div className='grid grid-cols-4 grid-rows-2'>
        <div className='flex flex-row col-span-2 my-2 mx-2'> Position </div>
        <div className='flex items-start my-2'>x: {Math.round(properties?.get('x') ?? 0)}</div>
        <div className='flex items-start my-2'>y: {Math.round(properties?.get('y') ?? 0)}</div>

        <div className='flex flex-row col-span-2 mx-2'> Scale </div>
        <div className='flex items-start'>x: {Math.round(properties?.get('width') ?? 0)}</div>
        <div className='flex items-start'>y: {Math.round(properties?.get('height') ?? 0)}</div>
      </div>
      <div>
        <p className='m-3 font-bold'>Image Description</p>
        <div className='overflow-auto flex items-start flex-wrap break-words'>{description || 'No description available.'}</div>
      </div>
      <div>
        <p className='m-3 font-bold'>Color Palette</p>
        <ColourPalette urls={urls} />
      </div>
    </div>
  )
}

export default ImageInspector
