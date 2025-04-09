import { useState, useEffect } from 'react'
import ReactDOM from 'react-dom'
import { getBackendUrl } from '../utils/env'

// Create a modal portal for the upload component
const ModalPortal = ({ children }) => {
  // Create a div that will be mounted to the body
  const modalRoot = document.getElementById('modal-root') || document.createElement('div')

  useEffect(() => {
    // Setup modal root if it doesn't exist
    if (!document.getElementById('modal-root')) {
      modalRoot.id = 'modal-root'
      document.body.appendChild(modalRoot)
    }

    return () => {
      // Clean up the div when the component unmounts if we created it
      if (modalRoot.parentNode && !document.getElementById('modal-root')) {
        document.body.removeChild(modalRoot)
      }
    }
  }, [])

  return ReactDOM.createPortal(children, modalRoot)
}

const UploadModal = ({ isOpen, onClose, userId = '123' }) => {
  const [file, setFile] = useState(null)
  const [description, setDescription] = useState('')
  const [fileClass, setFileClass] = useState('')
  const [colour, setColour] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const API_URL = getBackendUrl()

  const MAX_DESCRIPTION_LENGTH = 500

  // Valid classes for the dropdown
  const validClasses = [
    'art and film',
    'fabric',
    'fashion illustration',
    'garment',
    'historical photograph',
    'location photograph',
    'nature',
    'runway',
    'street style photograph',
    'texture'
  ]

  // Handle file selection
  const handleFileChange = async (e) => {
    const selectedFile = e.target.files[0]
    setFile(selectedFile)
    setUploadSuccess(false)
    setErrorMessage('')

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await fetch(`${API_URL}/api/files/analyze`, {
        method: 'POST',
        body: formData
      })

      const data = await response.json()

      if (data.success) {
        const parsedAnalysis = JSON.parse(data.analysis)
        const description = parsedAnalysis[0]
        const classification = parsedAnalysis[1]
        const colors = parsedAnalysis[2]
        console.log('Description:', description)
        console.log('Classification:', classification)
        console.log('Colors:', colors)
        setDescription(description)
        setFileClass(classification)
        setColour(colors)
      }
    } catch (error) {
      console.error('Error:', error)
    }
  }

  // Handle description change
  const handleDescriptionChange = (e) => {
    const text = e.target.value
    if (text.length <= MAX_DESCRIPTION_LENGTH) {
      setDescription(text)
    }
  }

  // Handle class selection
  const handleClassChange = (e) => {
    setFileClass(e.target.value)
  }

  // Handle colour change
  const handleColourChange = (e) => {
    setColour(e.target.value)
  }

  // Handle file upload using fetch API instead of axios
  const handleUpload = async () => {
    if (!file) {
      setErrorMessage('Please select a file to upload')
      return
    }

    setIsUploading(true)
    setErrorMessage('')

    const formData = new FormData()
    formData.append('file', file)
    formData.append('description', description)
    formData.append('user_id', userId)
    formData.append('class', fileClass)
    formData.append('colour', colour)

    try {
      const response = await fetch(`${API_URL}/api/files/upload`, {
        method: 'POST',
        body: formData
        // No need to set Content-Type header as fetch sets it correctly with boundary for FormData
      })

      if (!response.ok) {
        // Handle HTTP errors
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || `Upload failed with status: ${response.status}`)
      }

      const data = await response.json()

      if (data.description) setDescription(data.description)
      if (data.class) setFileClass(data.class)
      if (data.colour) setColour(data.colour)

      setIsUploading(false)
      setUploadSuccess(true)

      // Clear form after successful upload
      setFile(null)
      setDescription('')
      setFileClass('')
      setColour('')

      // Close the modal after a short delay to show success message
      setTimeout(() => {
        setUploadSuccess(false)
        onClose()
      }, 2000)
    } catch (error) {
      setIsUploading(false)
      setErrorMessage(error.message || 'Upload failed. Please try again.')
      console.error('Upload error:', error)
    }
  }

  // Prevent background scrolling when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }

    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  // Handle escape key to close modal
  useEffect(() => {
    const handleEsc = (event) => {
      if (event.key === 'Escape' && !isUploading) {
        onClose()
      }
    }

    window.addEventListener('keydown', handleEsc)

    return () => {
      window.removeEventListener('keydown', handleEsc)
    }
  }, [onClose, isUploading])

  if (!isOpen) return null

  // Label and input shared styles
  const labelStyle = {
    display: 'block',
    marginBottom: '8px',
    fontWeight: 600,
    color: '#374151',
    fontSize: '15px'
  }

  const inputStyle = {
    width: '100%',
    border: '1px solid #d1d5db',
    padding: '10px',
    borderRadius: '6px',
    backgroundColor: '#f9fafb',
    color: '#111827',
    fontSize: '15px'
  }

  const sectionStyle = {
    marginBottom: '24px'
  }

  // Use our custom portal component
  return (
    <ModalPortal>
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          backdropFilter: 'blur(3px)',
          zIndex: 10000,
          padding: '20px'
        }}
        onClick={(e) => {
          if (e.target === e.currentTarget && !isUploading) {
            onClose()
          }
        }}
      >
        <div
          style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '24px',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.2)',
            width: '100%',
            maxWidth: '450px',
            position: 'relative',
            maxHeight: '90vh',
            overflowY: 'auto'
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <h2
            style={{
              fontSize: '24px',
              fontWeight: 600,
              marginBottom: '20px',
              textAlign: 'center',
              color: '#333',
              borderBottom: '1px solid #eaeaea',
              paddingBottom: '10px'
            }}
          >
            Upload Image
          </h2>

          {/* File input */}
          <div style={sectionStyle}>
            <label style={labelStyle}>Select Image (PNG, JPG, JPEG, GIF)</label>
            <input type='file' accept='.png,.jpg,.jpeg,.gif' onChange={handleFileChange} style={inputStyle} disabled={isUploading} />
            {file && <p style={{ marginTop: '4px', fontSize: '14px', color: '#666' }}>Selected: {file.name}</p>}
          </div>

          {/* Description */}
          <div style={sectionStyle}>
            <label style={labelStyle}>Description</label>
            <textarea
              value={description}
              onChange={handleDescriptionChange}
              style={{
                ...inputStyle,
                minHeight: '100px',
                resize: 'vertical'
              }}
              maxLength={MAX_DESCRIPTION_LENGTH}
              disabled={isUploading}
              placeholder='Enter image description'
            ></textarea>
            <p
              style={{
                textAlign: 'right',
                fontSize: '14px',
                color: '#6B7280',
                marginTop: '6px',
                fontWeight: '500'
              }}
            >
              {description.length}/{MAX_DESCRIPTION_LENGTH}
            </p>
          </div>

          {/* Class Selection */}
          <div style={sectionStyle}>
            <label style={labelStyle}>Class</label>
            <select value={fileClass} onChange={handleClassChange} style={inputStyle} disabled={isUploading}>
              <option value=''>Select a class</option>
              {validClasses.map((cls) => (
                <option key={cls} value={cls}>
                  {cls.charAt(0).toUpperCase() + cls.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* Colour */}
          <div style={sectionStyle}>
            <label style={labelStyle}>Colour</label>
            <input
              type='text'
              value={colour}
              onChange={handleColourChange}
              style={inputStyle}
              disabled={isUploading}
              placeholder='Enter colour information'
            />
          </div>

          {/* Status messages */}
          {errorMessage && (
            <div
              style={{
                marginBottom: '16px',
                padding: '8px',
                backgroundColor: '#FEF2F2',
                border: '1px solid #FECACA',
                color: '#DC2626',
                borderRadius: '4px'
              }}
            >
              {errorMessage}
            </div>
          )}

          {uploadSuccess && (
            <div
              style={{
                marginBottom: '16px',
                padding: '8px',
                backgroundColor: '#F0FDF4',
                border: '1px solid #DCFCE7',
                color: '#16A34A',
                borderRadius: '4px'
              }}
            >
              File uploaded successfully!
            </div>
          )}

          {isUploading && (
            <div
              style={{
                marginBottom: '16px',
                padding: '8px',
                backgroundColor: '#EFF6FF',
                border: '1px solid #DBEAFE',
                color: '#2563EB',
                borderRadius: '4px',
                display: 'flex',
                alignItems: 'center'
              }}
            >
              <svg
                style={{
                  animation: 'spin 1s linear infinite',
                  marginRight: '12px',
                  height: '20px',
                  width: '20px'
                }}
                xmlns='http://www.w3.org/2000/svg'
                fill='none'
                viewBox='0 0 24 24'
              >
                <circle style={{ opacity: 0.25 }} cx='12' cy='12' r='10' stroke='currentColor' strokeWidth='4'></circle>
                <path
                  style={{ opacity: 0.75 }}
                  fill='currentColor'
                  d='M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z'
                ></path>
              </svg>
              Uploading... Please wait.
            </div>
          )}

          {/* Buttons */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'flex-end',
              gap: '8px',
              marginTop: '24px'
            }}
          >
            <button
              onClick={onClose}
              style={{
                padding: '10px 20px',
                border: '1px solid #d1d5db',
                borderRadius: '4px',
                backgroundColor: '#f3f4f6',
                color: '#4b5563',
                fontWeight: 500,
                cursor: isUploading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s ease',
                fontSize: '15px'
              }}
              onMouseOver={(e) => {
                if (!isUploading) e.currentTarget.style.backgroundColor = '#e5e7eb'
              }}
              onMouseOut={(e) => {
                if (!isUploading) e.currentTarget.style.backgroundColor = '#f3f4f6'
              }}
              disabled={isUploading}
            >
              Cancel
            </button>
            <button
              onClick={handleUpload}
              style={{
                padding: '10px 24px',
                backgroundColor: '#3B82F6',
                color: 'white',
                fontWeight: 500,
                border: 'none',
                borderRadius: '4px',
                cursor: isUploading || uploadSuccess ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s ease',
                fontSize: '15px'
              }}
              onMouseOver={(e) => {
                if (!(isUploading || uploadSuccess)) e.currentTarget.style.backgroundColor = '#2563eb'
              }}
              onMouseOut={(e) => {
                if (!(isUploading || uploadSuccess)) e.currentTarget.style.backgroundColor = '#3B82F6'
              }}
              disabled={isUploading || uploadSuccess}
            >
              Upload
            </button>
          </div>
        </div>
      </div>
      <style>
        {`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
      </style>
    </ModalPortal>
  )
}

export default UploadModal
