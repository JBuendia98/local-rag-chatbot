import { useState } from "react";

function App() {
  const [input, setInput] = useState("");
  const [response, setResponse] = useState("");

  const sendPrompt = async () => {
    setResponse("");

    const res = await fetch("http://127.0.0.1:8000/chat/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ prompt: input }),
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      setResponse((prev) => prev + decoder.decode(value));
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>Local LLM Chat</h1>

      <textarea
        rows={4}
        style={{ width: "100%" }}
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />

      <br />
      <button onClick={sendPrompt}>Send</button>

      <pre style={{ marginTop: "1rem", whiteSpace: "pre-wrap" }}>
        {response}
      </pre>
    </div>
  );
}

export default App;
