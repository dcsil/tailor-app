import { useState } from 'react'
import tailorLogo from './assets/tailor-blank-bg.png'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div>
        <img src={tailorLogo} className="" alt="Tailor logo" />
      </div>
      <h1>Hello World!</h1>
      <div className="card">
      <button onClick={() => {throw new Error("This is your first error!");}}>Break the world</button>
      </div>
      <p className="read-the-docs">
        Made using Vite
      </p>
    </>
  )
}

export default App
