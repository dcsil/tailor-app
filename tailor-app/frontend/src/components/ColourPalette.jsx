import React, { useState, useEffect } from 'react'
import ColorThief from 'colorthief'
import namer from 'color-namer'

// Helper functions for color conversions
const rgbToHex = (r, g, b) => `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase()}`

const hexToRgb = (hex) => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
      }
    : null
}

const rgbToCmyk = (r, g, b) => {
  const red = r / 255
  const green = g / 255
  const blue = b / 255

  const k = 1 - Math.max(red, green, blue)

  // Handle complete black case
  if (k === 1) {
    return { c: 0, m: 0, y: 0, k: 100 }
  }

  const c = Math.round(((1 - red - k) / (1 - k)) * 100)
  const m = Math.round(((1 - green - k) / (1 - k)) * 100)
  const y = Math.round(((1 - blue - k) / (1 - k)) * 100)
  const kPercent = Math.round(k * 100)

  return { c, m, y, k: kPercent }
}

// Pantone approximation
const approximatePantone = (r, g, b) => {
  const sum = r + g + b
  const pantoneNumber = Math.floor((sum / 765) * 900) + 100
  return `P ${pantoneNumber} C`
}

// Determine if text should be light or dark (based on background colour)
const getTextColour = (hexColour) => {
  const rgb = hexToRgb(hexColour)
  if (!rgb) return '#000000'

  // Rlative luminance
  const luminance = (0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b) / 255

  // If luminance is > 0.5 (i,e., background is light) => use dark text
  return luminance > 0.5 ? '#000000' : '#FFFFFF'
}

const ColourPalette = ({ urls }) => {
  const [allColours, setAllColours] = useState([])
  const [loading, setLoading] = useState(true)
  const [processedCount, setProcessedCount] = useState(0)

  useEffect(() => {
    // Reset state when URLs change
    setAllColours([])
    setLoading(true)
    setProcessedCount(0)

    // Skip if no URLs
    if (urls.length === 0) {
      setLoading(false)
      return
    }

    const colorThief = new ColorThief()
    let extractedColors = []

    urls.forEach((url) => {
      const img = new Image()
      img.crossOrigin = 'Anonymous' // Handle CORS issues ;-;

      img.onload = () => {
        try {
          // Get palette using ColorThief (returns array of RGB arrays)
          const palette = colorThief.getPalette(img, 10)

          // Convert RGB arrays to HEX strings (color-namer needs HEX)
          const hexColors = palette.map((color) => rgbToHex(color[0], color[1], color[2]))

          // Apply weighting to give more importance to dominant colors
          const weightedColors = []
          hexColors.forEach((color, index) => {
            const weight = Math.max(1, Math.floor(10 / (index + 1)))
            for (let i = 0; i < weight; i++) {
              weightedColors.push(color)
            }
          })

          // Add to the global collection
          extractedColors = [...extractedColors, ...weightedColors]

          // Update the state with the current collection
          setAllColours(extractedColors)

          // Update processed count
          setProcessedCount((prev) => {
            const newCount = prev + 1
            if (newCount === urls.length) {
              setLoading(false)
            }
            return newCount
          })
        } catch (err) {
          console.error('Error extracting colors:', err)
          setProcessedCount((prev) => {
            const newCount = prev + 1
            if (newCount === urls.length) {
              setLoading(false)
            }
            return newCount
          })
        }
      }

      img.onerror = () => {
        console.error(`Failed to load image: ${url}`)
        setProcessedCount((prev) => {
          const newCount = prev + 1
          if (newCount === urls.length) {
            setLoading(false)
          }
          return newCount
        })
      }

      // Start loading the image
      img.src = url
    })
  }, [urls])

  // Show loading
  if (loading)
    return (
      <p>
        Loading colour palette... ({processedCount}/{urls.length})
      </p>
    )

  // Count occurrences of each color across all images
  const colourCount = allColours.reduce((acc, color) => {
    acc[color] = (acc[color] || 0) + 1
    return acc
  }, {})

  // Sort colors by occurrence and take the top 5
  const topColours = Object.entries(colourCount)
    .sort((a, b) => b[1] - a[1]) // Sort by count
    .slice(0, 5) // Take top 5
    .map(([color]) => color) // Extract the hex values

  return (
    <div className='flex flex-col h-full'>
      <div className='flex flex-grow flex-col'>
        {topColours.length === 0 ? (
          <p className='flex-grow'>No colours found in images</p>
        ) : (
          topColours.map((colour, index) => {
            let colourName
            try {
              colourName = namer(colour).ntc[0].name
            } catch (e) {
              colourName = 'Unknown'
            }

            // For displaying the colour codes
            const rgb = hexToRgb(colour)
            const cmyk = rgbToCmyk(rgb.r, rgb.g, rgb.b)
            const pantone = approximatePantone(rgb.r, rgb.g, rgb.b)
            const textColor = getTextColour(colour)

            return (
              <div key={index} className='w-full h-full mb-1 p-1 text-left' style={{ backgroundColor: colour }}>
                <p className='font-medium' style={{ color: textColor }}>
                  {colourName.toUpperCase()}
                </p>
                {/* <p 
                  className="text-xs"
                  style={{ color: textColor }}
                >
                  HEX: {colour}
                </p> */}
                {/* <p 
                  className="text-xs"
                  style={{ color: textColor }}
                >
                  RGB: {rgb.r}, {rgb.g}, {rgb.b}
                </p> */}
                {/* <p 
                  className="text-xs"
                  style={{ color: textColor }}
                >
                  CMYK: {cmyk.c}%, {cmyk.m}%, {cmyk.y}%, {cmyk.k}%
                </p> */}
                <p className='text-xs' style={{ color: textColor }}>
                  {pantone}
                </p>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}

export default ColourPalette
