import { useState } from "react";

export function EditIcon(props) {
    return (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        width="1em"
        height="1em"
        {...props}
      >
        <g
          fill="none"
          stroke="currentColor"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="1.5"
        >
          <path d="M19.09 14.441v4.44a2.37 2.37 0 0 1-2.369 2.369H5.12a2.37 2.37 0 0 1-2.369-2.383V7.279a2.356 2.356 0 0 1 2.37-2.37H9.56"></path>
          <path d="M6.835 15.803v-2.165c.002-.357.144-.7.395-.953l9.532-9.532a1.36 1.36 0 0 1 1.934 0l2.151 2.151a1.36 1.36 0 0 1 0 1.934l-9.532 9.532a1.36 1.36 0 0 1-.953.395H8.197a1.36 1.36 0 0 1-1.362-1.362M19.09 8.995l-4.085-4.086"></path>
        </g>
      </svg>
    );
  };
  

const MoodboardTitle = ({ title, setTitle }) => {
    const [isEditing, setIsEditing] = useState(false);

    return (
        <div className="text-lg flex flex-row justify-center text-black mt-1 py-2">
            <div className="hover:bg-gray-300 px-3 py-1 rounded-md">
            {isEditing ? (
                <input
                    className="text-gray-700 bg-transparent border-b border-gray-500 outline-none"
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    onBlur={() => setIsEditing(false)}
                    autoFocus
                />
            ) : (
                <div className="flex flex-row items-center">
                <h1 
                    className="cursor-pointer"
                    onClick={() => setIsEditing(true)}
                >
                    {title}
                </h1>
                <EditIcon
                className="ml-2 cursor-pointer"
                onClick={() => setIsEditing(true)}/>
                </div>
            )}
            </div>
        </div>
    );
};

export default MoodboardTitle;
