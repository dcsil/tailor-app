import { Card, CardContent } from './Card'
import '../App.css'
import { useNavigate } from 'react-router-dom'

function CollectionItem({ title, files, image }) {
  const navigate = useNavigate()
  const handleSelect = () => {
    if (title === 'Uploads') {
      navigate('/mycollection/uploads', { state: { files } })
    } else if (title === 'Moodboards') {
      navigate('/mycollection/boards', { state: { files } })
    } else {
      navigate('/')
    }
  }

  return (
    <Card className='relative border border-gray-500 rounded-lg overflow-hidden flex items-center justify-center w-64 h-80 cursor-pointer'>
      <CardContent className='p-0 w-full h-full flex items-center justify-center relative'>
        {image ? <img src={image} alt={title} onClick={handleSelect} /> : <></>}
      </CardContent>
      <p className='absolute bottom-3 text-center w-full text-lg font-medium'>{title}</p>
    </Card>
  )
}

export default CollectionItem
