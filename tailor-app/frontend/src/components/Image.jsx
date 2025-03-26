/* eslint-disable */
import React, { useState, useRef, useEffect } from 'react';
import Draggable from 'react-draggable'; 
import { ResizableBox } from 'react-resizable';


const Image = ({id, src, initialX, initialY, initialWidth, initialHeight, boardClick, imageSelected, handleDelete, handleSelect}) => {

  const [position, setPosition] = useState({ x: initialX, y: initialY });
  const [dimensions, setDimensions] = useState({ width: initialWidth, height: initialHeight });
  // const [isSelected, setIsSelected] = useState(false);
  const imageRef = useRef(null);

  // handle selection locally
  const handleClick = (e) => {
      e.stopPropagation();
      handleSelect(id);
  };

  const handleResize = (e, {node, size, handle}) => {
    e.stopPropagation();
    setDimensions({ width: size.width, height: size.height});
  };
  
  const handleDrag = (e, ui) => {
    console.log(x.position)
    setPosition({x: x + ui.deltaX, y: y + ui.deltaY,})
    console.log(x.position)
  }

  // conditionally wrap with Draggable & ResizableBox if selected
  const content = (
    <img
      src={src}
      alt="Selectable"
      onClick={handleClick}
      style={{
        width: `${dimensions.width}px`,
        height: `${dimensions.height}px`,
        left: `${position.x}px`,
        top: `${position.y}px`,}}
    />
  );

  const deleteButton = (
    <div
      className="absolute top-0 right-0 w-4 h-4 bg-red-500 bg-opacity-60 cursor-pointer flex items-center justify-center hover:bg-opacity-80"
      onClick={(e) => {
        e.stopPropagation();
        handleDelete(id);
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
  );

  return  (
      <Draggable 
      cancel=".react-resizable-handle"
      onDragEnd={handleDrag}
      disabled={!imageSelected}
      >
      <ResizableBox 
        height={dimensions.height}
        width={dimensions.width}
        onResize={handleResize}
        resizeHandles={imageSelected ? ["se"] : []}
      >
      <div>
       {content}
       {imageSelected && (
        <div
            className="absolute top-0 right-0 w-4 h-4 bg-red-500 bg-opacity-60 cursor-pointer flex items-center justify-center hover:bg-opacity-80"
            onClick={(e) => {
              e.stopPropagation();
              handleDelete(id);
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
      )}

      </div>
      </ResizableBox>
      </Draggable>
  );
    // ) : (
    //   <div
    //   height={dimensions.height}
    //     width={dimensions.width}>
    //   {content}
    //   </div>
    // );
}
  
export default Image;
  