
// import { useState, useRef, useEffect } from "react";
// import axios from "axios";
// import "./App.css";

// export default function Confluence({ onSwitchToChatbot }) {
//   const [input, setInput] = useState("");
//   const [isLoading, setIsLoading] = useState(false);
//   const [listening, setListening] = useState(false);
//   const bottomRef = useRef(null);

//   const [messages, setMessages] = useState([
//     {
//       role: "assistant",
//       content: "👋 Hello! I'm your Confluence Assistant. Ask me anything about your documentation.",
//       timestamp: new Date().toLocaleTimeString(),
//     },
//   ]);

//   useEffect(() => {
//     bottomRef.current?.scrollIntoView({ behavior: "smooth" });
//   }, [messages]);

//   const sendMessage = async (textToSend = input) => {
//     if (!textToSend.trim() || isLoading) return;

//     const userMsg = {
//       role: "user",
//       content: textToSend,
//       timestamp: new Date().toLocaleTimeString(),
//     };
//     setMessages((prev) => [...prev, userMsg]);
//     setInput("");
//     setIsLoading(true);

//     try {
//       const res = await axios.post("http://localhost:5000/api/chat", {
//         query: textToSend,
//       });

//       let response = res.data.answer || "Sorry, I couldn't find an answer.";
//       // let source = "";

//       // if (response !== "Sorry, I couldn't find an answer." && res.data.title) {
//       //   source = `\n\n📄 Source: ${res.data.title}`;
//       // }

//       setMessages((prev) => [
//         ...prev,
//         {
//           role: "assistant",
//           content: `${response}`,
//           timestamp: new Date().toLocaleTimeString(),
//         },
//       ]);
//     } catch (err) {
//       console.error("API Error:", err);
//       setMessages((prev) => [
//         ...prev,
//         {
//           role: "assistant",
//           content: "⚠️ Error fetching response. Please try again.",
//           timestamp: new Date().toLocaleTimeString(),
//         },
//       ]);
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const handleKeyDown = (e) => {
//     if (e.key === "Enter" && !e.shiftKey) {
//       e.preventDefault();
//       sendMessage();
//     }
//   };

//   const startListening = () => {
//     if (!('webkitSpeechRecognition' in window)) {
//       alert("Speech recognition is not supported in this browser.");
//       return;
//     }

//     const recognition = new window.webkitSpeechRecognition();
//     recognition.lang = "en-US";
//     recognition.interimResults = false;
//     recognition.maxAlternatives = 1;

//     recognition.onstart = () => setListening(true);
//     recognition.onend = () => setListening(false);

//     recognition.onerror = (event) => {
//       console.error("Speech Recognition Error:", event.error);
//       alert("Speech recognition error: " + event.error);
//       setListening(false);
//     };

//     recognition.onresult = (event) => {
//       const transcript = event.results[0][0].transcript;
//       sendMessage(transcript);
//     };

//     recognition.start();
//   };

//   return (
//     <div className="chat-container">
//       <header className="chat-header">
//         <h1>Confluence Chatbot</h1>
//         <p className="subtitle">Ask questions about your documentation</p>
//       </header>

//       <div className="chat-messages">
//         {messages.map((msg, index) => (
//           <div key={index} className={`message ${msg.role}`}>
//             <div className="message-content">
//               {msg.content.split("\n").map((line, i) => (
//                 <p key={i}>{line}</p>
//               ))}
//             </div>
//             <div className="message-timestamp">{msg.timestamp}</div>
//           </div>
//         ))}
//         {isLoading && (
//           <div className="message assistant">
//             <div className="message-content">
//               <div className="typing-indicator">
//                 <span></span><span></span><span></span>
//               </div>
//             </div>
//           </div>
//         )}
//         <div ref={bottomRef} />
//       </div>

//       <div className="chat-input-container">
//         <input
//           type="text"
//           value={input}
//           onChange={(e) => setInput(e.target.value)}
//           onKeyDown={handleKeyDown}
//           placeholder="Ask about your Confluence docs..."
//           disabled={isLoading}
//         />
//         <button onClick={() => sendMessage()} disabled={isLoading || !input.trim()}>
//           {isLoading ? "..." : "Send"}
//         </button>
//         <button
//           onClick={startListening}
//           disabled={isLoading}
//           style={{ marginLeft: "10px" }}
//         >
//           {listening ? "🎤 Listening..." : "🎙 Speak"}
//         </button>
//         <button
//           onClick={onSwitchToChatbot}
//           style={{ marginLeft: "10px" }}
//         >
//           Live chat
//         </button>
//       </div>
//     </div>
//   );
// }
import { useState, useRef, useEffect } from "react";
import axios from "axios";
import ChatBot from "./ChatBot"; // Ensure this path is correct
import "./App.css";

export default function Confluence() {
  const [showChatBot, setShowChatBot] = useState(false);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const bottomRef = useRef(null);

  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "👋 Hello! I'm your Confluence Assistant. Ask me anything about your documentation.",
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (textToSend = input) => {
    if (!textToSend.trim() || isLoading) return;

    const userMsg = {
      role: "user",
      content: textToSend,
      timestamp: new Date().toLocaleTimeString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await axios.post("http://localhost:5000/api/chat", {
        query: textToSend,
      });

      let response = res.data.answer || "Sorry, I couldn't find an answer.";

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `${response}`,
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } catch (err) {
      console.error("API Error:", err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "⚠️ Error fetching response. Please try again.",
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const startListening = () => {
    if (!("webkitSpeechRecognition" in window)) {
      alert("Speech recognition is not supported in this browser.");
      return;
    }

    const recognition = new window.webkitSpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setListening(true);
    recognition.onend = () => setListening(false);

    recognition.onerror = (event) => {
      console.error("Speech Recognition Error:", event.error);
      alert("Speech recognition error: " + event.error);
      setListening(false);
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      sendMessage(transcript);
    };

    recognition.start();
  };

  if (showChatBot) {
    return <ChatBot onBack={() => setShowChatBot(false)} />;
  }

  return (
    <div className="chat-container">
      <header className="chat-header">
        <h1>Confluence Chatbot</h1>
        <p className="subtitle">Ask questions about your documentation</p>
      </header>

      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <div className="message-content">
              {msg.content.split("\n").map((line, i) => (
                <p key={i}>{line}</p>
              ))}
            </div>
            <div className="message-timestamp">{msg.timestamp}</div>
          </div>
        ))}
        {isLoading && (
          <div className="message assistant">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="chat-input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about your Confluence docs..."
          disabled={isLoading}
        />
        <button
          onClick={() => sendMessage()}
          disabled={isLoading || !input.trim()}
        >
          {isLoading ? "..." : "Send"}
        </button>
        <button
          onClick={startListening}
          disabled={isLoading}
          style={{ marginLeft: "10px" }}
        >
          {listening ? "🎤 Listening..." : "🎙 Speak"}
        </button>
        <button
          onClick={() => setShowChatBot(true)}
          style={{ marginLeft: "10px" }}
        >
          Live Chat
        </button>
      </div>
    </div>
  );
}
