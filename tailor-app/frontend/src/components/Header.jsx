
import { NavLink } from "react-router-dom";

const Header = () => {
    return (
        <div className="w-full p-1 font-[Apple Color Emoji] text-gray-300 text-sm flex justify-between items-center  border-gray-500">
            <NavLink to="/" className="text-xl"> 
            <h1>
                T<span className="font-extrabold tracking-widest text-white">AI</span>LOR
            </h1>
            </NavLink>
            <nav>
                <NavLink to="/mychat" className={({ isActive }) => `px-5 hover:text-white ${isActive ? "font-bold text-white" : ""}`}>Chats</NavLink>
                <NavLink to="/mycollection" className={({ isActive }) => `px-5 hover:text-white ${isActive ? "font-bold text-white" : ""}`}>Collections</NavLink>
                <NavLink to="/about" className={({ isActive }) => `px-5 hover:text-white ${isActive ? "font-bold text-white" : ""}`}>Account</NavLink>
            </nav>
        </div>
    );
};

export default Header