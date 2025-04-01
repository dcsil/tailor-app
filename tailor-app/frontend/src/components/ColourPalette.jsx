import { useExtractColors } from "react-extract-colors";
import namer from "color-namer";

import frankenpet from '../assets/frankenpet.png';

// const images = [frankenpet, frankenpet, frankenpet, frankenpet, frankenpet, frankenpet];

const ColourPalette = ({ urls }) => {
  // Extract colors for all images
  console.log("Image URLs:", urls);
  const extractedColors = urls.map((image) =>
    useExtractColors(image, {
      maxColors: 10,
      format: "hex",
      maxSize: 200,
      orderBy: "dominance",
    })
  );

  

  // Wait for colors to load
  if (extractedColors.some((res) => res.loading)) return <p>Loading colour palette...</p>;

  // Collect all colors into one array 
  let allColors = extractedColors.flatMap(({ colors }) => colors);

  // Count occurrences of each color
  const colorCount = allColors.reduce((acc, color) => {
    acc[color] = (acc[color] || 0) + 1;
    return acc;
  }, {});

  // Sort colors by occurrence and take the top 6
  const topColors = Object.entries(colorCount)
    .sort((a, b) => b[1] - a[1]) // Sort by count
    .slice(0, 5) // Take top 5
    .map(([color]) => color); // Extract the hex values 

  return (
    <div>
      {/* <div className="grid grid-cols-3 gap-2">
        {images.map((img, index) => (
          <img key={index} src={img} alt={`Image ${index + 1}`} width="100" height="100" />
        ))}
      </div> */}

      <div>
        {topColors.map((color, index) => {
          const colorName = namer(color).ntc[0].name; // Get detailed color name

          return (
            <div key={index} className="content-center w-35 h-15 mb-1" style={{ backgroundColor: color }}>
              <p className="text-sm font-medium">{colorName.toUpperCase()}</p>
              <p className="text-xs">{color}</p> {/* Display Hex Code */}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ColourPalette;
