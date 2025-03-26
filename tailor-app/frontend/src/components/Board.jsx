/* eslint-disable */
import React, { useState, useRef, useEffect } from 'react';
import Image from './Image';
// import ImageTest from './ImageTest';
import frankenpet from '../assets/frankenpet.png';

const Board = () => {

  const [images, setImages] = useState([
    { id: 1, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 1 },
    { id: 2, x: 250, y: 100, width: 200, height: 150, selected: false, zIndex: 2 },
    { id: 3, x: 150, y: 300, width: 120, height: 180, selected: false, zIndex: 3 },
    { id: 4, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 4 },
    { id: 5, x: 250, y: 100, width: 200, height: 150, selected: false, zIndex: 5 },
    { id: 6, x: 150, y: 300, width: 120, height: 180, selected: false, zIndex: 6 },
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

  // deselect on click
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
    <div className="flex flex-row p-4 gap-4">
      
      <div
        ref={boardRef}
        className="relative w-full max-w-6xl h-[85vh] border-2 border-gray-300 rounded bg-white overflow-hidden"
        onClick={handleBoardClick}
      >
        {images.map(img => (
          <Image
            key={img.id}
            src={frankenpet}
            id={img.id}
            initialX={img.x}
            initialY={img.y}
            //initialWidth={img.width}
            initialWidth={192}
            //initialHeight={img.height}
            initialHeight={300}
            zIndex={img.zIndex}
            isSelected={img.id === selectedId}
            onSelect={handleSelect}
            onDragEnd={handleDragEnd}
            onResize={handleResize}
          />
        ))}
      </div>
      <div className="flex flex-col justify-start mb-2 mx-3">
        <button
          className="px-10 py-2 border-1 my-3 text-white rounded-xl shadow-lg hover:bg-gray-300 focus:outline-none"
          onClick={handleAddImage}
        >
          Insert
        </button>
        <button
          className="px-10 py-2 border-1 my-3 text-white rounded-xl shadow-lg hover:bg-gray-300 focus:outline-none"
          onClick={handleAddImage}
        >
          Export
        </button>
      </div>


    </div>
  );
};

export default Board;