import ReactMarkdown from 'react-markdown'
import '../markdown.css'

const FormattedAnalysis = ({ analysis }) => {
  return (
    <div className='markdown-body max-w-full overflow-x-auto'>
      <ReactMarkdown>{analysis}</ReactMarkdown>
    </div>
  )
}

export default FormattedAnalysis
