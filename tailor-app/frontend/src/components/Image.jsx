/* eslint-disable */
import React, { useState, useRef, useEffect } from 'react';
import Draggable from 'react-draggable'; 
import { ResizableBox } from 'react-resizable';

const Image = ({id, CustomComponent, properties, imageIdSelected, handleDelete, handleSelect, imageEdit, bringToFront, boardRef, urls}) => {
  const [position, setPosition] = useState({ x: properties.get('x'), y: properties.get('y') });
  const [dimensions, setDimensions] = useState({ width: properties.get('width'), height: properties.get('height') });
  const [isSelected, setIsSelected]= useState(false);

  const imageRef = useRef(null);

  useEffect(() => {
    if (imageRef.current) {
      const rect = imageRef.current.getBoundingClientRect();
      setPosition({x:rect.x, y:rect.y});
      setDimensions({width: rect.width, height:rect.height});
      imageEdit(id, Math.round(rect.width), Math.round(rect.height), Math.round(rect.x), Math.round(rect.y), true);
    }
  }, []);

  // check if current image is selected
  useEffect(() => {
    if (id == imageIdSelected){
      setIsSelected(true);
    } else{ setIsSelected(false); }
  }, [imageIdSelected])

  // handle selection locally
  const onClick = (e) => {
    e.stopPropagation();
    handleSelect(id);
    bringToFront(id);
  };

  const onResize = (e, {node, size, handle}) => {
    //e.stopPropagation();
    bringToFront(id);
    setDimensions({ width: size.width, height: size.height});
    imageEdit(id, size.width, size.height, position.x, position.y, true);
  };
  
  const onDrag = (e, ui) => {
    bringToFront(id);
    const rect = imageRef.current.getBoundingClientRect();
    setPosition({x: position.x + ui.deltaX, y: position.y + ui.deltaY,})
    imageEdit(id, dimensions.width, dimensions.height, Math.round(rect.x), Math.round(rect.y), true);
  }

  // conditionally wrap with Draggable & ResizableBox if selected
  // + choose either CustomComponent or Image
  const content = (
    <div
      ref={imageRef}
      onClick={onClick}
      style={{
        width: `${dimensions.width}px`,
        height: `${dimensions.height}px`,
        // left: `${position.x}px`,
        // top: `${position.y}px`,
        // //position: 'absolute',
      }} 
    >
      {CustomComponent ? (
        // Render the custom React component
        React.cloneElement(CustomComponent, { urls: urls })
        ) : (
        // Render the image if no CustomComponent is provided
        <img
        
          src={properties.get('url')}
          alt="Selectable"
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
          }}
          draggable="false"
          onDragStart={(e) => e.preventDefault()}
        />
      )}
    </div>
  );

  return  (
    <div   style={{ zIndex: properties.get('zIndex'),
      // width: `${dimensions.width}px`,
      //   height: `${dimensions.height}px`,
      //   left: `${position.x}px`,
      //   top: `${position.y}px`,
      //   position: 'absolute',
        pointerEvents: 'auto',
        visibility: properties.get('isVisible')? 'visible':'hidden'
,    }}
    >
      <Draggable 
      cancel=".react-resizable-handle"
      onDrag={onDrag}
      disabled={!isSelected}
      >
      <ResizableBox 
        height={dimensions.height}
        width={dimensions.width}
        onResize={onResize}
        resizeHandles={isSelected ? ["se"] : []}
      >
      <div>
       {content}
       {isSelected && (
        
        //  delete button
        <div
            className="absolute top-0 right-0 w-4 h-4 bg-red-500 bg-opacity-60 cursor-pointer flex items-center justify-center hover:bg-opacity-80"
            onClick={(e) => {
              e.stopPropagation();
              imageEdit(id, dimensions.width, dimensions.height, position.x, position.y, false);
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
    </div>
  );

}
  
export default Image;
  