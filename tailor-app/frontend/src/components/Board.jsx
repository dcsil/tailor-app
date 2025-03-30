/* eslint-disable */
import React, { useState, useRef, useEffect } from 'react';
import Image from './Image';
import { getBackendUrl } from '../utils/env.js';

// images
// import activity from '../assets/UI placeholders/activity.jpeg';
// import fabric from '../assets/UI placeholders/fabric.jpeg';
// import fabric1 from '../assets/UI placeholders/fabric1.jpeg';
// import hair from '../assets/UI placeholders/hair.jpeg';
// import interior from '../assets/UI placeholders/interior.jpeg';
// import palette from '../assets/UI placeholders/palette.jpeg';
// import scenery from '../assets/UI placeholders/scenery.jpeg';
// import style from '../assets/UI placeholders/style.jpeg';
// import runway from '../assets/UI placeholders/runway.jpeg';
// import runway2 from '../assets/UI placeholders/runway2.jpeg';
// import runway3 from '../assets/UI placeholders/runway3.jpeg';
// import runway4 from '../assets/UI placeholders/runway4.jpeg';

const BoardTest = (props) => {
    
    // const [images, setImages] = useState([
    //     { id: 1, src: activity, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 1 },
    //     { id: 2, src: fabric, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 2 },
    //     { id: 3, src: runway2, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 3},
    //     { id: 4, src: hair, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 4 },
    //     { id: 5, src: style, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 5 },
    //     { id: 6, src: palette, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 6},
    //     { id: 7, src: runway3, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 7 },
    //     { id: 8, src: interior, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 8 },
    //     { id: 9, src: runway, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 9 },
    //     { id: 10, src: fabric1, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 10 },
    //     { id: 11, src: scenery, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 11 },
    //     { id: 12, src: runway4, x: 50, y: 50, width: 90, height: 50, selected: false, zIndex: 12 },
    //   ]);
    const API_URL = getBackendUrl();
    const [prompt, setPrompt] = useState(props.prompt)
    const [ids, setIds] = useState(props.ids);
    const [images, setImages] = useState(props.urls);
    
    const [selectedId, setSelectedId] = useState(null);
    const boardRef = useRef(null);
    const nextId = useRef(13);
    const nextZIndex = useRef(13);

    // Deselect on click
    const handleBoardClick = () => {
      setSelectedId(null);
    };

    // Select on click 
    const handleSelect = (id) => {
      bringToFront(id);
      setSelectedId(id);
    };

    const handleDelete = (id) => {
      setImages(images.filter(img => img.id !== id));
      setSelectedId(null);
      return;
    }

    const handleAddImage = async () => {
      const response = await fetch(`${API_URL}/api/regenerate-search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: prompt.trim() }),
      });
      const data = await response.json();
      if (data.error) throw new Error(data.error);

      const [next_image_id, next_image_url] = data.next_image;
      setIds((prevIds) => [...prevIds, next_image_id]); 
      setImages((prevImages) => [...prevImages, next_image_url]); 
    }

    const handleExport = () => {

    }
    // const handleResize = (id, width, height) => {
    //   const currentZ = nextZIndex.current;
    //   setImages(images.map(img => 
    //     { if (img.id === id) {
    //       return { ...img, width, height, zIndex: currentZ };
    //     }
    //     return img;}

    //   ));
    //   nextZIndex.current += 1;
    //   setSelectedId(id);
    // };
  
    const bringToFront = (id) => {
      const currentZ = nextZIndex.current;
      setImages(images.map(img => 
            { if (img.id === id) {
              console.log(img.zIndex);
              return { ...img, zIndex: currentZ };
              
            }
            return img;}
    
          ));
      nextZIndex.current += 1;
      setSelectedId(id);
    };

    return (
        <div className="flex flex-row p-4">
          <div
            ref={boardRef}
            className="relative w-full grid grid-cols-6 grid-rows-2 max-w-6xl h-[85vh] border-2 border-gray-300 rounded bg-white overflow-hidden"
            onClick={handleBoardClick}
          >
            {images.map((img, index) => (
                <div key={ids[index]} className="col-span-1 row-span-1">
                    <Image
                    className="w-full h-full object-cover"
                        id={ids[index]}
                        src={img}
                        initialX={0}
                        initialY={0}
                        initialWidth={200}
                        initialHeight={320}
                        imageSelected={img.id === selectedId}
                        handleDelete={handleDelete}
                        handleSelect={handleSelect}
                        bringToFront={bringToFront}
                    />
                </div>
            ))}
           
          </div>
    

          <div className="flex flex-col justify-start mb-2 mx-5">
            <button
              className="px-10 py-2 border-1 my-3 text-white rounded-3xl shadow-md shadow-gray-600 hover:bg-gray-300 focus:outline-none"
              onClick={handleAddImage}
            >
              Generate
            </button>
            <button
              className="px-10 py-2 border-1 my-3 text-white rounded-3xl shadow-md shadow-gray-600 hover:bg-gray-300 focus:outline-none"
              onClick={handleExport}
            >
              Export
            </button>
          </div>
    
        </div>
    );

}


export default BoardTest;