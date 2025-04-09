import { NavLink } from 'react-router-dom'
import ReactTooltip from 'react-tooltip';

const Header = () => {
  return (
    <div className='header w-full p-1 font-[Apple Color Emoji] text-gray-300 text-sm flex justify-between items-center mb-10'>
      <NavLink to='/' className='text-xl cursor-pointer' data-tip="Go to main page">
        <h1>
          T<span className='font-extrabold tracking-widest text-white'>AI</span>LOR
        </h1>
      </NavLink>
      <nav>
        {/* <NavLink
          to='/mychat'
          state={{ fetchData: true }}
          className={({ isActive }) => `px-5 hover:text-white cursor-pointe ${isActive ? 'font-bold text-white' : ''}`}
        >
          Chats
        </NavLink> */}
        <NavLink
          to='/mycollection'
          className={({ isActive }) => `px-5 hover:text-white cursor-pointe ${isActive ? 'font-bold text-white' : ''}`}
          data-tip="Go to uploads and boards"
        >
          Collections
        </NavLink>
        <NavLink to='/login' className={({ isActive }) => `px-5 hover:text-white cursor-pointe ${isActive ? 'font-bold text-white' : ''}`}>
          Account
        </NavLink>
      </nav>
      <ReactTooltip place="top" type="dark" effect="solid" />
    </div>
  )
}

export default Header
