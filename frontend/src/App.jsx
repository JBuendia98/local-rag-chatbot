import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { dracula } from "react-syntax-highlighter/dist/esm/styles/prism";

const MarkdownRenderer = ({ content }) => {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        code({ node, inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || "");
          return !inline && match ? (
            <SyntaxHighlighter
              style={dracula}
              language={match[1]}
              PreTag="div"
              {...props}
            >
              {String(children).replace(/\n$/, "")}
            </SyntaxHighlighter>
          ) : (
            <code className="bg-gray-200 text-red-600 px-1 py-0.5 rounded text-sm font-mono" {...props}>
              {children}
            </code>
          );
        },
        a: ({ node, ...props }) => <a className="text-blue-600 hover:underline" {...props} />
      }}
    >
      {content}
    </ReactMarkdown>
  );
};

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const abortControllerRef = useRef(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const stopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  };

  const sendPrompt = async () => {
    if (!input.trim()) return;

    const controller = new AbortController();
    abortControllerRef.current = controller;

    const userMessage = { role: "user", text: input };
    setInput("");
    setLoading(true);

    setMessages((prev) => [
      ...prev, 
      userMessage, 
      { role: "ai", text: "" }
    ]);

    try {
      const res = await fetch("http://127.0.0.1:8000/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: userMessage.text }),
        signal: controller.signal, 
      });

      if (!res.ok) throw new Error("Network error");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let aiText = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        aiText += decoder.decode(value, { stream: true });

        setMessages((prev) => {
          const updated = [...prev];
          const lastIndex = updated.length - 1;
          updated[lastIndex] = { 
            ...updated[lastIndex], 
            text: aiText 
          };
          return updated;
        });
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log("Generation stopped by user");
        setMessages((prev) => {
            const updated = [...prev];
            const lastIndex = updated.length - 1;
            updated[lastIndex] = {
              ...updated[lastIndex],
              text: updated[lastIndex].text + " 🛑 [Stopped]"
          };
            return updated;
        });
      } else {
        console.error(error);
        setMessages((prev) => [...prev, { role: "ai", text: "Error: Could not fetch response." }]);
      }
    } finally {
      setLoading(false);
      abortControllerRef.current = null;
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100 font-sans">
      {/* Header */}
      <header className="bg-white border-b px-6 py-4 text-lg font-bold text-gray-800 shadow-sm flex items-center gap-2">
        <span>🤖</span> Local LLM Chat
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
                  px-5 py-3 rounded-2xl shadow-sm max-w-[85%] overflow-hidden
                  ${
                    msg.role === "user"
                      ? "bg-blue-600 text-white rounded-br-none"
                      : "bg-white text-gray-800 border border-gray-200 rounded-bl-none"
                  }
                `}
              >
                {msg.role === "ai" ? (
                  <div className="markdown-body text-sm leading-relaxed">
                    <MarkdownRenderer content={msg.text} />
                  </div>
                ) : (
                  <div className="whitespace-pre-wrap">{msg.text}</div>
                )}
              </div>
            </div>
          ))}

          {loading && (
             <div className="flex justify-start animate-pulse">
               <div className="text-gray-400 text-sm italic ml-2">Thinking...</div>
            </div>
          )}
          
          <div ref={bottomRef} />
        </div>
      </main>

      {/* Input Footer */}
      <footer className="bg-white border-t p-4">
        <div className="max-w-3xl mx-auto flex gap-3 items-end">
          <textarea
            className="flex-1 resize-none bg-gray-100 border-0 rounded-2xl p-4 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all disabled:opacity-60 disabled:cursor-not-allowed"
            rows={1}
            placeholder={loading ? "Wait for response..." : "Type your message..."}
            value={input}
            disabled={loading} 
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
                if(e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendPrompt();
                }
            }}
          />
          
          {loading ? (
             <button
                onClick={stopGeneration}
                className="bg-red-500 text-white px-6 py-3 rounded-xl font-semibold hover:bg-red-600 transition-colors mb-1 shadow-md"
             >
               Stop
             </button>
          ) : (
             <button
                onClick={sendPrompt}
                disabled={!input.trim()}
                className="bg-blue-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed mb-1 shadow-md"
             >
               Send
             </button>
          )}
        </div>
      </footer>
    </div>
  );
}

export default App;