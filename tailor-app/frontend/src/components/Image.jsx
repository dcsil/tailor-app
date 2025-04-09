/* eslint-disable */
import React, { useState, useRef, useEffect } from 'react'
import Draggable from 'react-draggable'
import { ResizableBox } from 'react-resizable'

const Image = ({
  id,
  CustomComponent,
  properties,
  imageIdSelected,
  handleDelete,
  handleSelect,
  imageEdit,
  bringToFront,
  saveToHistory,
  historyDone,
  isRefreshHistory,
  boardRef,
  urls
}) => {
  const [position, setPosition] = useState({ x: properties.get('x'), y: properties.get('y') })
  const [dimensions, setDimensions] = useState({ width: properties.get('width'), height: properties.get('height') })
  const [isSelected, setIsSelected] = useState(false)

  const divRef = useRef(null)

  // check if current image is selected
  useEffect(() => {
    if (id == imageIdSelected) {
      setIsSelected(true)
    } else {
      setIsSelected(false)
    }
  }, [imageIdSelected])

  // refresh history
  useEffect(() => {
    if (isRefreshHistory) {
      setPosition({ x: properties.get('x'), y: properties.get('y') })
      setDimensions({ width: properties.get('width'), height: properties.get('height') })
      historyDone()
    }
  }, [isRefreshHistory])

  // handle selection locally
  const onClick = (e) => {
    e.stopPropagation()
    handleSelect(id)
    bringToFront(id)
  }

  const onResize = (e, { node, size, handle }) => {
    //e.stopPropagation();
    bringToFront(id)
    setDimensions({ width: size.width, height: size.height })
    imageEdit(id, size.width, size.height, position.x, position.y, true)
  }

  const onDrag = (e, ui) => {
    //e.stopPropagation();
    bringToFront(id)
    setPosition({ x: position.x + ui.deltaX, y: position.y + ui.deltaY })
    imageEdit(id, dimensions.width, dimensions.height, position.x + ui.deltaX, position.y + ui.deltaY, true)
  }

  // conditionally wrap with Draggable & ResizableBox if selected
  const content = (
    <img
      src={properties.get('url')}
      alt='Selectable'
      style={{
        width: '100%',
        height: '100%',
        objectFit: 'fill'
      }}
      draggable='false'
      onDragStart={(e) => e.preventDefault()}
    />
  )

  return (
    <Draggable cancel='.react-resizable-handle' onStop={saveToHistory} onDrag={onDrag} disabled={!isSelected}>
      <div
        ref={divRef}
        onClick={onClick}
        style={{
          zIndex: properties.get('zIndex'),
          width: `${dimensions.width}px`,
          height: `${dimensions.height}px`,
          left: `${position.x}px`,
          top: `${position.y}px`,
          position: 'absolute',
          visibility: properties.get('isVisible') ? 'visible' : 'hidden'
        }}
      >
        <ResizableBox
          height={dimensions.height}
          width={dimensions.width}
          onResize={onResize}
          onResizeStop={saveToHistory}
          resizeHandles={isSelected ? ['se'] : []}
        >
          <div
            style={{
              width: '100%',
              height: '100%'
            }}
          >
            {content}
            {isSelected && (
              //  delete button
              <div
                className='absolute top-0 right-0 w-4 h-4 bg-red-500 bg-opacity-60 cursor-pointer flex items-center justify-center hover:bg-opacity-80'
                onClick={(e) => {
                  e.stopPropagation()
                  handleDelete(id)
                }}
              >
                <svg
                  xmlns='http://www.w3.org/2000/svg'
                  width='10'
                  height='10'
                  viewBox='0 0 24 24'
                  fill='none'
                  stroke='white'
                  strokeWidth='2'
                  strokeLinecap='round'
                >
                  <line x1='18' y1='6' x2='6' y2='18'></line>
                  <line x1='6' y1='6' x2='18' y2='18'></line>
                </svg>
              </div>
            )}
          </div>
        </ResizableBox>
      </div>
    </Draggable>
  )
}

export default Image
