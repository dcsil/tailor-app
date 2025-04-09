import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import ReactTooltip from 'react-tooltip'
import { getBackendUrl } from '../utils/env.js'

// Assets
import { Search, Paperclip, Send, Loader2 } from 'lucide-react'

// Components

const PromptInput = () => {
  const [prompt, setPrompt] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()
  const API_URL = getBackendUrl()

  const handleSend = async () => {
    if (!prompt.trim()) return

    setIsLoading(true)

    try {
      const response = await fetch(`${API_URL}/api/search-prompt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: prompt.trim(), template: 'basic_chat' })
      })

      const data = await response.json()
      if (data.error) throw new Error(data.error)

      // Navigate to moodboard page
      navigate('/moodboardresult', { state: { prompt: prompt.trim(), response: data } })
    } catch (error) {
      console.error('Error:', error)
      navigate('/moodboardresult', { state: { prompt: prompt.trim(), response: 'Error processing request.' } })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className='w-[70vw]'>
      {/* Text Input Area */}
      <div className='relative'>
        <Search className='absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5' />
        <input
          type='text'
          placeholder='How can I inspire you?'
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className='w-full py-4 px-12 rounded-2xl bg-white text-black placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-300'
        />
      </div>

      {/* Action Buttons */}
      <div className='flex justify-end mt-4 space-x-2'>
        {/* <button className='px-4 py-2 bg-white text-black rounded-full hover:bg-gray-200 flex items-center space-x-2'>
          <Paperclip className='w-5 h-5' />
          <span>Attach</span>
        </button> */}

        {/* Send prompt */}
        <button onClick={handleSend} disabled={isLoading} className='px-4 py-2 bg-gray-900 rounded-full hover:bg-gray-800 outline-solid' data-tip="Click to generate mood board for your prompt">
          {isLoading ? <Loader2 className='w-5 h-5 text-white animate-spin' /> : <Send className='w-5 h-5 text-white' />}
        </button>
        <ReactTooltip place="top" type="dark" effect="solid" />
      </div>
    </div>
  )
}

export default PromptInput
