import { useState, useRef, useEffect } from "react";

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendPrompt = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    const res = await fetch("http://127.0.0.1:8000/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: userMessage.text }),
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder();

    let aiText = "";
    setMessages((prev) => [...prev, { role: "ai", text: "" }]);

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      aiText += decoder.decode(value);
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1].text = aiText;
        return updated;
      });
    }

    setLoading(false);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100 font-sans">
      {/* Header */}
      <header className="bg-white border-b px-6 py-4 text-lg font-bold text-gray-800 shadow-sm">
        🤖 Local LLM Chat
      </header>
  
      {/* Chat Container */}
      <main className="flex-1 overflow-y-auto p-4">
        <div className="max-w-3xl mx-auto space-y-6">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`
                  px-5 py-3 rounded-2xl shadow-sm 
                  max-w-[80%]  /* FIX 1: Prevent bubbles from being too wide */
                  whitespace-pre-wrap /* FIX 2: Respect newlines and lists */
                  ${
                    msg.role === "user"
                      ? "bg-blue-600 text-white rounded-br-none"
                      : "bg-white text-gray-800 border border-gray-200 rounded-bl-none"
                  }
                `}
              >
                {msg.text}
              </div>
            </div>
          ))}
  
          {loading && (
            <div className="flex justify-start">
               <div className="text-gray-400 text-sm italic ml-2">AI is thinking...</div>
            </div>
          )}
  
          <div ref={bottomRef} />
        </div>
      </main>
  
      {/* Input Footer */}
      <footer className="bg-white border-t p-4">
        <div className="max-w-3xl mx-auto flex gap-3 items-end"> {/* FIX 3: Align button to bottom */}
          <textarea
            className="flex-1 resize-none bg-gray-100 border-0 rounded-2xl p-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all"
            rows={1}
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            // Optional: Auto-expand height or handle Enter key here
          />
          <button
            onClick={sendPrompt}
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed mb-1"
          >
            Send
          </button>
        </div>
      </footer>
    </div>
  );
}

export default App;
