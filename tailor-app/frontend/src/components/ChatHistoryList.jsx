import ChatHistory from './ChatHistory'

const ChatHistoryList = (props) => {
  return (
    <div className='my-3 overflow-y-auto'>
      {props.chatHistory.map((c) => (
        <ChatHistory key={c._id} title={c.prompt} date={new Date(c.timestamp * 1000).toLocaleDateString()} />
      ))}
    </div>
  )
}

export default ChatHistoryList
