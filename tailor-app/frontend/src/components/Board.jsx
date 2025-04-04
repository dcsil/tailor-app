/* eslint-disable */
import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Image from './Image';
import { getBackendUrl } from '../utils/env.js';
import { toBlob } from 'html-to-image';

// Components
import ColourPalette from './ColourPalette.jsx';
import SuccessBanner from './SuccessBanner.jsx';
import MoodboardTitle from './MoodboardTitle.jsx';
import ImageInspector from './ImageInspector.jsx';

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

// icons
import UndoIcon from '../utils/SVG Icons/UndoIcon'
import ExportIcon from '../utils/SVG Icons/ExportIcon'
import AddIcon from '../utils/SVG Icons/AddIcon'

const BoardTest = (props) => {
    
    const API_URL = getBackendUrl();
    const navigate = useNavigate();
    const [prompt, setPrompt] = useState(props.prompt)
    const [ids, setIds] = useState(props.ids);
    const [images, setImages] = useState(props.urls);
    const [title, setTitle] = useState("My Moodboard");

    const [imageMap, setImageMap] = useState(new Map());
    const [zIndexCounter, setZIndexCounter] = useState(0);


    const [zIndexMap, setZIndexMap] = useState({}); 

    const [selectedId, setSelectedId] = useState(null);

    const [showPalette, setShowPalette] = useState(false);
    const [successExport, setSuccessExport] = useState(false);
    const boardRef = useRef(null);

    useEffect(() => {
      setImageMap((prevMap) => {
        const newImageData = new Map(prevMap);
        
        ids.forEach((id, index) => {
          // Check if the id already exists in the map
          if (!newImageData.has(id)) {
            // If it doesn't exist, set it with the new values
            newImageData.set(id, new Map([
              ['url', images[index]],
              ['width', 170],
              ['height', 300],
              ['x',  0],
              ['y', 0],
              ['zIndex', zIndexCounter + index],
            ]));
          }
        });
        return newImageData;
      }) 
      setZIndexCounter(zIndexCounter+ids.length);
    }, [ids]);


    // useEffect(() => {
    //   if (props.ids.length > 0) {
    //     let maxZ = 0;
    //     const initialZIndexMap = props.ids.reduce((acc, id, index) => {
    //       const zIndex = index + 1; // Set z-index in order of appearance
    //       acc[id] = zIndex
    //       maxZ = Math.max(maxZ, zIndex);
    //       return acc;
    //     }, {});

    //     console.log(JSON.stringify(initialZIndexMap, null, 2));
    //     console.log('max Z: '+maxZ);

    //     setZIndexMap(initialZIndexMap);
    //     setHighestZIndex(maxZ);
    //   }
    // }, [props.ids]); // Runs when ids change
    

    // Deselect on click
    const handleBoardClick = () => {
      setSelectedId(null);
    };

    // Select on click 
    const handleSelect = (id) => {
      setSelectedId(id);
      console.log("selected ID in board:  " + id)
    };

    const imageEdit = (id, width, height, x, y) => {
      setImageMap(prevMap => {
        const updatedMap = new Map(prevMap); 
        if (updatedMap.has(id)) {
          const image = updatedMap.get(id);
          image.set('width', width);
          image.set('height', height);
          image.set('x', x);
          image.set('y', y);
          updatedMap.set(id, image);
          return updatedMap;
        }
        return prevMap
      });
    };

    const handleDelete = (id) => {

      setImages((prevImages) => prevImages.filter((_, index) => index !== ids.indexOf(id)));
      setIds((prevIds) => prevIds.filter((item) => item !== id));
      setImageMap((prevData) => {
        const newData = new Map(prevData);
        newData.delete(id);
        return newData;
      });
      
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
    

    const handleExport = async () => {
  if (!boardRef.current) {
    console.error("Export failed: Board reference not found");
    return;
  }

  setSelectedId(null);
  setShowPalette(false);

  try {
    await new Promise(resolve => setTimeout(resolve, 300));

    const blob = await toBlob(boardRef.current, {
      quality: 1, 
      pixelRatio: 2, 
      backgroundColor: 'transparent',
    });

    if (!blob) {
      throw new Error("Failed to generate image blob");
    }

    const formData = new FormData();
    formData.append("file", blob, `${title}.png`);
    formData.append("user_id", "123"); // TODO: fix later
    formData.append("image_ids", ids);
    formData.append("prompt", prompt);

    await Promise.all([
      fetch(`${API_URL}/api/boards/upload`, {
        method: "POST",
        body: formData,
      }),
      
      (() => {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${title}.png`;
        document.body.appendChild(link);
        link.click();
        setTimeout(() => {
          document.body.removeChild(link);
          URL.revokeObjectURL(url);
        }, 100);
      })()
    ]);

    setSuccessExport(true);
    setTimeout(() => navigate("/"), 2000);

  } catch (error) {
    console.error("Export failed:", error);
  }
    };

    const bringToFront = (id) => {
      setImageMap((prevData) => {
        const newData = new Map(prevData);
        const updatedImageData = new Map(newData.get(id));

        updatedImageData.set('zIndex', zIndexCounter);
        newData.set(id, updatedImageData);
  
        return newData;
      });
      setZIndexCounter((prev) => prev + 1);
    };

    return (
      <>
        <MoodboardTitle title={title} setTitle={setTitle}/>
        <div className="flex flex-col p-1 max-w-full">

          <div className="flex flex-row justify-start gap-3 mb-4 mx-5">

            <button className="flex items-center gap-4 px-3 py-1.5 rounded-xl border-gray-600 border-2 hover:bg-gray-300 cursor-pointer"
            onClick={handleExport}> 
            <ExportIcon/>
            Download
            </button>

            <button className="flex items-center gap-3 px-3 py-1.5 rounded-xl border-gray-600 border-2 hover:bg-gray-300 cursor-pointer" 
            onClick={handleAddImage}
            >
            <AddIcon/>
            Add
            </button>

            <button className="flex items-center gap-4 px-3 py-1.5 rounded-xl border-gray-600 border-2 hover:bg-gray-300 cursor-pointer"> 
            <UndoIcon/>
            Undo
            </button>

        </div>

        <div className="flex flex-row gap-4">
          <div
            ref={boardRef}
            className=" w-full relative grid grid-cols-6 grid-rows-2 max-h-[80vh] border-2 border-gray-300 rounded bg-white overflow-hidden"
            //rgrid grid-cols-6 grid-rows-2
            onClick={handleBoardClick}
          >
            {Array.from(imageMap).map(([key, innerMap]) => (
              <Image
                //className="col-span-1 row-span-1 object-fill"
                key={key}
                id={key}
                properties={innerMap}
                // initialX={0}
                // initialY={0}
                // initialWidth={170}
                // initialHeight={300}
                imageSelected={selectedId}
                handleDelete={handleDelete}
                handleSelect={handleSelect}
                bringToFront={bringToFront}
                imageEdit={imageEdit}
                boardRef={boardRef}
                // zIndex={zIndexMap[ids[index]] || 1}
              />
            ))}
            
            {showPalette && <Image
              className="w-full h-full object-cover"
              key={100}
              id={100}
              CustomComponent={<ColourPalette />}
              initialX={0}
              initialY={0}
              initialWidth={170}
              initialHeight={300}
              imageSelected={selectedId}
              handleDelete={handleDelete}
              handleSelect={handleSelect}
              imageEdit={imageEdit}
              bringToFront={bringToFront}
              boardRef={boardRef}
              zIndex={100}
              urls={images}
            />}
            {successExport && <SuccessBanner message="Export was successful!" />}
            </div>
            <div>
         <ImageInspector
         properties={imageMap.get(selectedId)}/>
        </div>
          </div>
        </div>
        </>
    );

}


export default BoardTest;