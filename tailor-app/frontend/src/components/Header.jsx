
import { NavLink } from "react-router-dom";

const Header = () => {
    return (
        <div className="w-full p-2 font-mono text-gray-300 text-sm flex justify-between items-center border-b-1 border-white">
            <NavLink to="/" className="text-l text-white"> 
            <h1>
                T<span className="font-extrabold">AI</span>LOR
            </h1>
            </NavLink>
            <nav>
                <NavLink to="/mychat" className={({ isActive }) => `px-4 hover:text-white ${isActive ? "font-bold text-white" : ""}`}>My Chats</NavLink>
                <NavLink to="/mycollection" className={({ isActive }) => `px-4 hover:text-white ${isActive ? "font-bold text-white" : ""}`}>My Collection</NavLink>
                <NavLink to="/about" className={({ isActive }) => `px-4 hover:text-white ${isActive ? "font-bold text-white" : ""}`}>My Account</NavLink>
            </nav>
        </div>
    );
};

export default Header