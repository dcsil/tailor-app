import PropTypes from 'prop-types'

const ChatHistory = (props) => {
  return (
    <div className='my-7 border-1 border-gray-200 rounded-3xl hover:bg-gray-400 hover:font-bold'>
      <div className='p-5 flex flex-row justify-between'>
        <span>{props.title}</span>
        <span>{props.date}</span>
      </div>
    </div>
  )
}

ChatHistory.propTypes = {
  title: PropTypes.string.isRequired,
  date: PropTypes.string.isRequired
}

export default ChatHistory
