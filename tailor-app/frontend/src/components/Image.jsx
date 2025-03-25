/* eslint-disable */
import React, { useState, useRef, useEffect } from 'react';

const Image = ({ id, src, initialX, initialY, initialWidth, initialHeight, zIndex, isSelected, onSelect, onDragEnd, onResize }) => {
   
    const [position, setPosition] = useState({ x: initialX, y: initialY });
    const [dimensions, setDimensions] = useState({ width: initialWidth, height: initialHeight });
    const [isDragging, setIsDragging] = useState(false);
    const [isResizing, setIsResizing] = useState(false);
    const [resizeType, setResizeType] = useState(null); // 'corner', 'horizontal', or 'vertical'
    const [isHovered, setIsHovered] = useState(false);
    const imageRef = useRef(null);
    const dragStartPos = useRef({ x: 0, y: 0 });
    const resizeStartDimensions = useRef({ width: 0, height: 0 });
    const resizeStartPos = useRef({ x: 0, y: 0 });
    const wasDragging = useRef(false);
    const initialClick = useRef(true);
    const movementThreshold = 3; // Add a small threshold for movement detection
  
    const handleMouseDown = (e) => {
      // Don't start dragging if clicking on any resize handle
      if (e.target.closest('.resize-handle')) {
        return;
      }
  
      e.stopPropagation();
  
      // Select the image immediately on mousedown
      onSelect(id);
  
      // Reset dragging flag
      wasDragging.current = false;
  
      // Start dragging
      setIsDragging(true);
      dragStartPos.current = {
        x: e.clientX - position.x,
        y: e.clientY - position.y
      };
    };
  
    // Handle click to prevent deselection when clicking on the image
    const handleClick = (e) => {
      // Prevent the click from propagating to the board
      e.stopPropagation();
  
      // Don't trigger selection if we were just dragging
      if (!wasDragging.current) {
        onSelect(id);
      }
    };
  
    // Handle mouse down for resizing
    const handleResizeMouseDown = (type) => (e) => {
      e.stopPropagation();
      e.preventDefault();
  
      // Select the image immediately on mousedown
      onSelect(id);
  
      // Start resizing with specified type
      setResizeType(type);
      setIsResizing(true);
      initialClick.current = true;
      resizeStartDimensions.current = {
        width: dimensions.width,
        height: dimensions.height,
        aspectRatio: dimensions.width / dimensions.height
      };
      resizeStartPos.current = {
        x: e.clientX,
        y: e.clientY
      };
    };
  
    // Effect for handling mouse move and up events
    useEffect(() => {
      const handleMouseMove = (e) => {
        if (isDragging) {
          wasDragging.current = true;
          const newX = e.clientX - dragStartPos.current.x;
          const newY = e.clientY - dragStartPos.current.y;
          setPosition({ x: newX, y: newY });
        }
  
        if (isResizing) {
          const dx = e.clientX - resizeStartPos.current.x;
          const dy = e.clientY - resizeStartPos.current.y;
  
          // Only apply resize if movement exceeds threshold or we're past the initial click
          if (initialClick.current && Math.abs(dx) < movementThreshold && Math.abs(dy) < movementThreshold) {
            return;
          }
  
          // We've moved past the initial click threshold
          initialClick.current = false;
  
          // Update dimensions based on resize type
          if (resizeType === 'corner') {
            // For corner resize, maintain aspect ratio
            const aspectRatio = resizeStartDimensions.current.aspectRatio;
  
            // Choose the dimension with the larger relative change
            // This makes resizing feel more natural based on primary movement direction
            const relativeWidthChange = Math.abs(dx / resizeStartDimensions.current.width);
            const relativeHeightChange = Math.abs(dy / resizeStartDimensions.current.height);
  
            if (relativeWidthChange >= relativeHeightChange) {
              // Width-driven resize
              const newWidth = Math.max(50, resizeStartDimensions.current.width + dx);
              const newHeight = newWidth / aspectRatio;
              setDimensions({ width: newWidth, height: newHeight });
            } else {
              // Height-driven resize
              const newHeight = Math.max(50, resizeStartDimensions.current.height + dy);
              const newWidth = newHeight * aspectRatio;
              setDimensions({ width: newWidth, height: newHeight });
            }
          } else if (resizeType === 'horizontal') {
            // Horizontal resize only
            const newWidth = Math.max(50, resizeStartDimensions.current.width + dx);
            setDimensions({ ...dimensions, width: newWidth });
          } else if (resizeType === 'vertical') {
            // Vertical resize only
            const newHeight = Math.max(50, resizeStartDimensions.current.height + dy);
            setDimensions({ ...dimensions, height: newHeight });
          }
        }
      };
  
      const handleMouseUp = (e) => {
        if (isDragging) {
          setIsDragging(false);
          onDragEnd(id, position);
  
          // Prevent any click events from firing on the board
          e.stopPropagation();
  
          // Keep selection after dragging
          onSelect(id);
        }
  
        if (isResizing) {
          setIsResizing(false);
          setResizeType(null);
          initialClick.current = true;
  
          // Only call onResize if we actually changed dimensions
          if (!initialClick.current) {
            onResize(id, dimensions.width, dimensions.height);
          }
        }
      };
  
      if (isDragging || isResizing) {
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
      }
  
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }, [isDragging, isResizing, resizeType, id, onDragEnd, onResize, position, dimensions, onSelect]);
  
    return (
      <div
        ref={imageRef}

        className={`absolute flex items-center justify-center select-none
          ${isSelected ? 'ring-2 ring-blue-500' : ''}
          ${isDragging ? 'shadow-xl' : 'shadow-md'}`}
        style={{
          width: `${dimensions.width}px`,
          height: `${dimensions.height}px`,
          left: `${position.x}px`,
          top: `${position.y}px`,
          //backgroundColor: '#f0f0f0',
          transform: isDragging ? 'scale(1.02)' : 'scale(1)',
          transition: isDragging ? 'none' : 'transform 0.2s, box-shadow 0.2s',
          zIndex: zIndex,
          cursor: isResizing ? (
            resizeType === 'horizontal' ? 'ew-resize' : 
            resizeType === 'vertical' ? 'ns-resize' : 
            'nwse-resize'
          ) : (isDragging ? 'grabbing' : 'grab')
        }}
        onMouseDown={handleMouseDown}
        onClick={handleClick}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <img
            ref={imageRef}
            src={src}
            alt="Image"
            style={{ 
            width: `${dimensions.width}px`,
            height: `${dimensions.height}px`,
          }}
          />  
        {/* show when selected */}
        {isSelected && (
          <>
            {/* delete button */}
            <div
              className="absolute top-0 right-0 w-4 h-4 bg-red-500 bg-opacity-60 cursor-pointer flex items-center justify-center hover:bg-opacity-80"
              onClick={(e) => {
                e.stopPropagation();
                onDragEnd(id, { x: -9999, y: -9999 }); // Signal to parent to delete this image
              }}
            >
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                width="10" 
                height="10" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="white" 
                strokeWidth="2" 
                strokeLinecap="round" 
              >
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </div>
  
            {/* Corner resize handle */}
            <div
              className="resize-handle absolute bottom-0 right-0 w-4 h-4 bg-black bg-opacity-20 cursor-se-resize flex items-center justify-center hover:bg-opacity-50"
              onMouseDown={handleResizeMouseDown('corner')}
            >
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                width="10" 
                height="10" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2" 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                className="text-white"
              >
                <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="m4.5 4.5 15 15m0 0V8.25m0 11.25H8.25"
                    />
              </svg>
            </div>
  
            {/* Right edge resize handle (horizontal) */}
            <div
              className="resize-handle absolute top-1/2 right-0 w-1 h-8 -ml-4 bg-black bg-opacity-20 cursor-ew-resize flex items-center justify-center hover:bg-opacity-50"
              onMouseDown={handleResizeMouseDown('horizontal')}
            >
            </div>

            {/* Left edge resize handle (horizontal) */}
            <div
              className="resize-handle absolute top-1/2 left-0 w-1 h-8 -mr-4 bg-black bg-opacity-20 cursor-ew-resize flex items-center justify-center hover:bg-opacity-50"
              onMouseDown={handleResizeMouseDown('horizontal')}
            >
            </div>
  
            {/* Bottom edge resize handle (vertical) */}
            <div
              className="resize-handle absolute bottom-0 left-1/2 w-8 h-1 -ml-4 bg-black bg-opacity-20 cursor-ns-resize flex items-center justify-center hover:bg-opacity-50"
              onMouseDown={handleResizeMouseDown('vertical')}
            >
            </div>

            {/* Top edge resize handle (vertical) */}
            <div
              className="resize-handle absolute top-0 left-1/2 w-8 h-1 -ml-4 bg-black bg-opacity-20 cursor-ns-resize flex items-center justify-center hover:bg-opacity-50"
              onMouseDown={handleResizeMouseDown('vertical')}
            >
            </div>
            
          </>
        )}
      </div>
    );
  };

  export default Image;