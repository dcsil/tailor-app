import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { getBackendUrl } from '../utils/env.js'

// styling
import '../App.css'
import { X } from 'lucide-react'

function BoardCollection() {
  const API_URL = getBackendUrl()
  const userId = '123'
  const location = useLocation()
  const navigate = useNavigate()
  const state_files = location.state?.files || []
  const [files, setFiles] = useState(state_files)
  const [selectedImage, setSelectedImage] = useState(null)

  async function handleBoardDelete(board_id) {
    const response = await fetch(`${API_URL}/api/boards/${userId}/${board_id}`, { method: 'DELETE' })
    const data = await response.json()

    if (data.error) throw new Error(data.error)
    setFiles((prevFiles) => prevFiles.filter((file, _) => file._id !== board_id))
  }

  return (
    <div className='container mx-auto px-4 py-8'>
      {/* Breadcrumb Navigation */}
      <nav className='sticky top-0 z-50 bg-gray-900  py-4 mb-8 shadow-lg shadow-purple-500/30'>
        <ol className='flex items-center space-x-3 text-lg'>
          <li>
            <button
              onClick={() => navigate('/mycollection')}
              className='text-gray-500 hover:text-white transition-colors duration-200 cursor-pointer'
            >
              My Collection
            </button>
          </li>
          <li aria-hidden='true' className='text-white'>
            {'>'}
          </li>
          <li className='text-white font-medium' aria-current='page'>
            Boards
          </li>
        </ol>
      </nav>

      {/* boards Grid */}
      <section className='w-full'>
        {files && files.length > 0 ? (
          <div className='grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-4 gap-6'>
            {files.map((board) => (
              <article key={board._id} className='group relative flex flex-col h-[70%]'>
                <div className='relative aspect-square black overflow-hidden'>
                  <img
                    id={board._id}
                    alt={board.boardname}
                    src={board.blob_url}
                    className='max-w-full max-h-full object-cover'
                    onClick={() => setSelectedImage(board)}
                  />

                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleBoardDelete(board._id)
                    }}
                    className='absolute top-2 right-2 bg-black/70 text-white p-1 rounded-full hover:bg-red-500 transition-all duration-200 opacity-0 group-hover:opacity-100 focus:opacity-100'
                  >
                    <X size={18} />
                  </button>
                </div>

                {/* Description container */}
                <div className='mt-2 p-2 flex-1 flex flex-col'>
                  <p className='text-white text-sm font-medium truncate' title={board.boardname}>
                    {board.boardname}
                  </p>
                  <time className='text-gray-400 text-xs mt-1'>{new Date(board.timestamp).toLocaleDateString()}</time>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <p className='text-gray-400 text-center py-12'>No boards found</p>
        )}
      </section>

      {selectedImage && (
        <div className='fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4' onClick={() => setSelectedImage(null)}>
          <div className='relative max-w-full max-h-full' onClick={(e) => e.stopPropagation()}>
            <img src={selectedImage.blob_url} width={'auto'} height={'auto'} alt={selectedImage.boardname} />

            <button
              className='absolute top-1 right-1 bg-black/70 text-white p-2 rounded-full hover:bg-red-500 transition-all'
              onClick={() => setSelectedImage(null)}
            >
              <X size={24} />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default BoardCollection
