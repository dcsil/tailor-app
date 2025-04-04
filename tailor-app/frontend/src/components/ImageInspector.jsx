/* eslint-disable */
import React, { useState, useRef, useEffect } from 'react';
import Draggable from 'react-draggable'; 
import { ResizableBox } from 'react-resizable';

const ImageInspector =({properties}) => {
    //const [position, setPosition] = useState({ x: properties?.get('x') ?? 0, y: properties?.get('y') ?? 0 });
    //const [dimensions, setDimensions] = useState({ width: properties?.get('width') ?? 0, height: properties?.get('height') ?? 0 });
   
    return (
    <div className="max-h-[80vh] border-2 border-gray-300 rounded min-w-xs bg-white">
        <p>Properties</p>
        <div className="grid grid-cols-4 grid-rows-2">
            <div className="flex flex-row col-span-2 my-2 mx-2"> Position </div>
            <div className="flex items-start my-2">x: {properties?.get('x') ?? 0}</div>
            <div className="flex items-start my-2">y: {properties?.get('y') ?? 0}</div>
  

            <div className="flex flex-row col-span-2 mx-2"> Scale </div>
            <div className="flex items-start">x: {properties?.get('width') ?? 0}</div>
            <div className="flex items-start">y: {properties?.get('height') ?? 0}</div>
            
            </div>



       
    </div>
    )
}

export default ImageInspector;