/* eslint-disable */
import React, { useState, useRef, useEffect } from 'react';
import Draggable from 'react-draggable'; 
import { ResizableBox } from 'react-resizable';

const Image = ({id, src, CustomComponent, properties, imageSelected, handleDelete, handleSelect, imageEdit,bringToFront, boardRef, urls}) => {
  const [position, setPosition] = useState({ x: properties.get('x'), y: properties.get('y') });
  const [dimensions, setDimensions] = useState({ width: properties.get('width'), height: properties.get('height') });
  const [isSelected, setIsSelected]= useState(false);
  const [history, setHistory] = useState([]);

  const imageRef = useRef(null);

  useEffect(()=>{
    const rect = imageRef.current.getBoundingClientRect();
    setDimensions({ width: rect.width, height: rect.height});
    setPosition({x: rect.left, y:rect.top});
    console.log(rect)
  }, []);

  useEffect(() => {
    if (id == imageSelected){
      setIsSelected(true);
      
    } else{ setIsSelected(false); }
  }, [imageSelected])


  // handle selection locally
  const onClick = (e) => {
    const rect = imageRef.current.getBoundingClientRect();
    console.log(rect)
    setDimensions({ width: rect.width, height: rect.height});
    setPosition({x: rect.left, y:rect.top});

    e.stopPropagation();
    handleSelect(id);
    imageEdit(id, dimensions.width, dimensions.height, position.x, position.y);
    bringToFront(id);
  };

  const onResize = (e, {node, size, handle}) => {
    e.stopPropagation();
    setDimensions({ width: size.width, height: size.height});
    imageEdit(id, size.width, size.height, position.x, position.y);
    bringToFront(id);
  };
  
  const onDrag = (e, ui) => {
    bringToFront(id);
    setPosition({x: position.x + ui.deltaX, y: position.y + ui.deltaY,})
    imageEdit(id, dimensions.width, dimensions.height, position.x + ui.deltaX, position.y + ui.deltaY);
  }

  const undo = () => {
    if (history.length > 0) {
      const lastState = history[history.length - 1];
      setDimensions(lastState.dimensions);
      setPosition(lastState.position);

      // Remove the last state from history after undoing
      setHistory(history.slice(0, -1));
    }
  };



  // conditionally wrap with Draggable & ResizableBox if selected
  // const content = (
  //   <img
  //     src={src}
  //     alt="Selectable"
  //     onClick={onClick}
  //     style={{
  //       width: `${dimensions.width}px`,
  //       height: `${dimensions.height}px`,
  //       left: `${position.x}px`,
  //       top: `${position.y}px`,}}
  //   />
  // );

  // conditionally wrap with Draggable & ResizableBox if selected
  // + choose either CustomComponent or Image
  const content = (
    <div
      onClick={onClick}
      // style={{
      //   // position: 'relative',
      //   width: `${dimensions.width}px`,
      //   height: `${dimensions.height}px`,
      //   left: `${position.x}px`,
      //   top: `${position.y}px`,
      //   position: 'absolute',
      //   pointerEvents: 'auto'
      // }}
      
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
    <div ref={imageRef} style={{ zIndex: properties.get('zIndex'),
      width: `${dimensions.width}px`,
        height: `${dimensions.height}px`,
        left: `${position.x}px`,
        top: `${position.y}px`,
        position: 'absolute',
        pointerEvents: 'auto'
    }}>
      <Draggable 
      cancel=".react-resizable-handle"
      onDragEnd={onDrag}
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
      </div>
  );

}
  
export default Image;
  