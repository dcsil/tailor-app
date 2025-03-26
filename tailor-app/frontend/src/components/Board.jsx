/* eslint-disable */
import React, { useState, useRef, useEffect } from 'react';
import Image from './Image';

// images
import activity from '../assets/UI placeholders/activity.jpeg';
import fabric from '../assets/UI placeholders/fabric.jpeg';
import fabric1 from '../assets/UI placeholders/fabric1.jpeg';
import hair from '../assets/UI placeholders/hair.jpeg';
import interior from '../assets/UI placeholders/interior.jpeg';
import palette from '../assets/UI placeholders/palette.jpeg';
import scenery from '../assets/UI placeholders/scenery.jpeg';
import style from '../assets/UI placeholders/style.jpeg';
import runway from '../assets/UI placeholders/runway.jpeg';
import runway2 from '../assets/UI placeholders/runway2.jpeg';
import runway3 from '../assets/UI placeholders/runway3.jpeg';
import runway4 from '../assets/UI placeholders/runway4.jpeg';

const BoardTest = () => {
    
    const [images, setImages] = useState([
        { id: 1, src: activity, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 1 },
        { id: 2, src: fabric, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 1 },
        { id: 3, src: runway2, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 1 },
        { id: 4, src: hair, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 1 },
        { id: 5, src: style, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 1 },
        { id: 6, src: palette, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 1 },
        { id: 7, src: runway3, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 1 },
        { id: 8, src: interior, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 1 },
        { id: 9, src: runway, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 1 },
        { id: 10, src: fabric1, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 1 },
        { id: 11, src: scenery, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 1 },
        { id: 12, src: runway4, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 1 },
      ]);
    
    const [selectedId, setSelectedId] = useState(null);
    const boardRef = useRef(null);

    // Deselect on click
    const handleBoardClick = () => {
      setSelectedId(null);
      console.log('here');
    };

    // Select on click 
    const handleSelect = (id) => {
      setSelectedId(id);
    };

    const handleDelete = (id) => {
      setImages(images.filter(img => img.id !== id));
      setSelectedId(null);
      return;
    }

    return (
        <div className="flex flex-row p-4">
          <div
            ref={boardRef}
            className="relative w-full grid grid-cols-6 grid-rows-2 max-w-6xl h-[85vh] border-2 border-gray-300 rounded bg-white overflow-hidden"
            onClick={handleBoardClick}
          >
            {images.map(img => (
                <div key={img.id} className="col-span-1 row-span-1">
                    <Image
                    className="w-full h-full object-cover"
                        id={img.id}
                        src={img.src}
                        initialX={0}
                        initialY={0}
                        initialWidth={200}
                        initialHeight={320}
                        imageSelected={img.id === selectedId}
                        handleDelete={handleDelete}
                        handleSelect={handleSelect}
                    />
                </div>
            ))}
           
          </div>
    

          <div className="flex flex-col justify-start mb-2 mx-5">
            <button
              className="px-10 py-2 border-1 my-3 text-white rounded-3xl shadow-md shadow-gray-600 hover:bg-gray-300 focus:outline-none"
              //onClick={handleAddImage}
            >
              Generate
            </button>
            <button
              className="px-10 py-2 border-1 my-3 text-white rounded-3xl shadow-md shadow-gray-600 hover:bg-gray-300 focus:outline-none"
            >
              Export
            </button>
          </div>
    
        </div>
    );

}


export default BoardTest;