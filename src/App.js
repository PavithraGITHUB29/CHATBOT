// import React, { useState } from 'react';
// import Confluence from './Confluence';
// import ChatBot from './ChatBot';

// function App() {
//   const [showChatBot, setShowChatBot] = useState(false);

//   return (
//     <div className="App">
//       {!showChatBot ? (
//         <Confluence onSwitchToChatbot={() => setShowChatBot(true)} />
//       ) : (
//         <ChatBot />
//       )}
//     </div>
//   );
// }

// export default App;
import React, { useState } from 'react';
import Confluence from './Confluence';
import ChatBot from './ChatBot';

function App() {
  const [showChatBot, setShowChatBot] = useState(false);

  return (
    <div className="App">
      {!showChatBot ? (
        <Confluence onSwitchToChatbot={() => setShowChatBot(true)} />
      ) : (
        <ChatBot onBack={() => setShowChatBot(false)} />
      )}
    </div>
  );
}

export default App;
