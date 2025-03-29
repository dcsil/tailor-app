/* eslint-disable */
import ChatHistory from './ChatHistory';

const ChatHistoryList = (props) => {
    return (
        <div className="my-3 overflow-y-auto">
      {props.chatHistory.map(c => <ChatHistory key={c.id} title={c.title} date={c.date}/>)}
     </div> 
    );
};

export default ChatHistoryList