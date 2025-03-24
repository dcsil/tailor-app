import React, { useState, useRef, useEffect } from 'react';

const Image = ({ id, initialX, initialY, initialWidth, initialHeight, zIndex, isSelected, onSelect, onDragEnd, onResize }) => {
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

  // Handle mouse down for dragging
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
        backgroundColor: '#f0f0f0',
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
      <div className="font-medium text-gray-700">Image</div>
      
      {/* Show resize handles and delete button only when selected */}
      {isSelected && (
        <>
          {/* Delete button (X) in top right corner */}
          <div
            className="absolute top-0 right-0 w-8 h-8 bg-red-500 bg-opacity-60 cursor-pointer flex items-center justify-center hover:bg-opacity-80 transition-colors"
            onClick={(e) => {
              e.stopPropagation();
              onDragEnd(id, { x: -9999, y: -9999 }); // Signal to parent to delete this image
            }}
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              width="16" 
              height="16" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="white" 
              strokeWidth="2" 
              strokeLinecap="round" 
              strokeLinejoin="round"
            >
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </div>
          
          {/* Corner resize handle (diagonal) */}
          <div
            className="resize-handle absolute bottom-0 right-0 w-8 h-8 bg-blue-500 bg-opacity-20 cursor-se-resize flex items-center justify-center hover:bg-opacity-50"
            onMouseDown={handleResizeMouseDown('corner')}
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              width="16" 
              height="16" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2" 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              className="text-blue-500"
            >
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            </svg>
          </div>
          
          {/* Right edge resize handle (horizontal) */}
          <div
            className="resize-handle absolute top-1/2 right-0 w-8 h-8 -mt-4 bg-blue-500 bg-opacity-20 cursor-ew-resize flex items-center justify-center hover:bg-opacity-50"
            onMouseDown={handleResizeMouseDown('horizontal')}
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              width="16" 
              height="16" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2" 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              className="text-blue-500"
            >
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </div>
          
          {/* Bottom edge resize handle (vertical) */}
          <div
            className="resize-handle absolute bottom-0 left-1/2 w-8 h-8 -ml-4 bg-blue-500 bg-opacity-20 cursor-ns-resize flex items-center justify-center hover:bg-opacity-50"
            onMouseDown={handleResizeMouseDown('vertical')}
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              width="16" 
              height="16" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2" 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              className="text-blue-500"
            >
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <polyline points="19 12 12 19 5 12"></polyline>
            </svg>
          </div>
        </>
      )}
    </div>
  );
};

// MoodBoard component
const MoodBoard = () => {
  const [images, setImages] = useState([
    { id: 1, x: 50, y: 50, width: 150, height: 150, selected: false, zIndex: 1 },
    { id: 2, x: 250, y: 100, width: 200, height: 150, selected: false, zIndex: 2 },
    { id: 3, x: 150, y: 300, width: 120, height: 180, selected: false, zIndex: 3 },
  ]);
  const [selectedId, setSelectedId] = useState(null);
  const nextId = useRef(4);
  const nextZIndex = useRef(4); // Track highest z-index
  const boardRef = useRef(null);

  // Select an image and bring it to front
  const handleSelect = (id) => {
    setSelectedId(id);
    bringToFront(id);
  };

  // Brings the selected image to the front by updating z-index
  const bringToFront = (id) => {
    const currentZ = nextZIndex.current;
    setImages(images.map(img => 
      img.id === id ? { ...img, zIndex: currentZ } : img
    ));
    nextZIndex.current += 1;
  };

  // Deselect when clicking on the board
  const handleBoardClick = () => {
    setSelectedId(null);
  };

  // Add a new image
  const handleAddImage = () => {
    const newImage = {
      id: nextId.current,
      x: Math.random() * 300 + 50,
      y: Math.random() * 200 + 50,
      width: Math.random() * 100 + 100,
      height: Math.random() * 100 + 100,
      selected: false,
      zIndex: nextZIndex.current
    };
    setImages([...images, newImage]);
    nextId.current += 1;
    nextZIndex.current += 1;
  };

  // Update image position after drag ends or handle deletion
  const handleDragEnd = (id, newPosition) => {
    // Check if this is a delete operation (special position used as a signal)
    if (newPosition.x === -9999 && newPosition.y === -9999) {
      // Delete the image
      setImages(images.filter(img => img.id !== id));
      setSelectedId(null);
      return;
    }
    
    // Normal drag operation
    const currentZ = nextZIndex.current;
    setImages(images.map(img => 
      img.id === id ? { ...img, x: newPosition.x, y: newPosition.y, zIndex: currentZ } : img
    ));
    nextZIndex.current += 1;
    // Keep the image selected after dragging
    setSelectedId(id);
  };
  
  // Handle image resize
  const handleResize = (id, width, height) => {
    const currentZ = nextZIndex.current;
    setImages(images.map(img => 
      img.id === id ? { ...img, width, height, zIndex: currentZ } : img
    ));
    nextZIndex.current += 1;
    // Keep the image selected after resizing
    setSelectedId(id);
  };

  return (
    <div className="flex flex-col items-center p-4 gap-4">
      <div className="flex gap-4 mb-4">
        <button
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 focus:outline-none"
          onClick={handleAddImage}
        >
          Add Image
        </button>
      </div>
      
      <div
        ref={boardRef}
        className="relative w-full max-w-4xl h-96 border-2 border-gray-300 rounded bg-white overflow-hidden"
        onClick={handleBoardClick}
      >
        {images.map(img => (
          <Image
            key={img.id}
            id={img.id}
            initialX={img.x}
            initialY={img.y}
            initialWidth={img.width}
            initialHeight={img.height}
            zIndex={img.zIndex}
            isSelected={img.id === selectedId}
            onSelect={handleSelect}
            onDragEnd={handleDragEnd}
            onResize={handleResize}
          />
        ))}
      </div>
      
      <div className="text-sm text-gray-500 mt-2">
        Click and drag to move • Click to select • Corner handle preserves aspect ratio
      </div>
    </div>
  );
};

export default MoodBoard;