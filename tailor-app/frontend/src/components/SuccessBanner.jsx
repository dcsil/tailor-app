import React, { useState, useEffect } from 'react';

const SuccessBanner = ({ message }) => {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false); // Hide banner after 3 seconds
    }, 3000);

    return () => clearTimeout(timer); // Cleanup on component unmount
  }, []);

  if (!visible) return null; // Don't render the banner if it's not visible

  return (
    <div style={styles.banner}>
      <p>{message}</p>
    </div>
  );
};

const styles = {
    banner: {
      position: 'fixed',
      top: 0,               
      left: '50%',        
      transform: 'translateX(-50%)', 
      width: '50%',
      backgroundColor: 'green',
      color: 'white',
      padding: '10px',
      textAlign: 'center',
      zIndex: 1000,
    },
};
  
  

export default SuccessBanner;
