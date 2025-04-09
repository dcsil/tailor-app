// import the hook
import { useExtractColors } from "react-extract-colors";
import frankenpet from '../assets/frankenpet.png'

const ColourPicker = () => {
  // Use the hook to extract the dominant color
  const { colors } = useExtractColors(frankenpet, {
    maxColors: 10,
    format: "hex",
    maxSize: 200,
    orderBy: "dominance",
  });

  const colorPalette = colors.map(( color, index ) => 
        <div style={{ backgroundColor: color }}>{index}</div>
    );

  return (
    // set a linear gradient with colors extracted
    <div>
        <img src={frankenpet} alt="random image" width="200" height="300" />
        
        {colorPalette}
    </div>
  );
};

export default ColourPicker;