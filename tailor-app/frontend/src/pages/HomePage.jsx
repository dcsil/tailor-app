// Assets and styling
import '../App.css'

// Components
import PromptInput from '../components/PromptInput'

function HomePage() {
  return (
    <div className='flex flex-col items-center text-white'>
      <div className='mb-16 mt-5 masking-container'>
        <h1 className='masked-text'>TAILOR</h1>
        {/* <img src={tailorLogo} className="mx-auto" alt="Tailor logo" /> */}
      </div>
      <PromptInput />
    </div>
  )
}

export default HomePage
