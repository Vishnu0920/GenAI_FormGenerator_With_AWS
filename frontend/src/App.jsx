import React, { useState, useEffect } from "react";
import "./App.css";

const API_BASE_URL = "http://localhost:5000";

function App() {
  const [prompt, setPrompt] = useState("");
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const [model, setModel] = useState("");
  const [models, setModels] = useState([]);

  useEffect(() => {
    // Fetch available models from backend
    fetch(`${API_BASE_URL}/api/models`)
      .then((res) => res.json())
      .then((data) => {
        // Filter out Deepseek if present
        const filtered = data.filter((m) => m.value !== "deepseek-r1");
        setModels(filtered);
        if (filtered.length > 0) setModel(filtered[0].value);
      })
      .catch(() => setError("Failed to load models"));
  }, []);

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError("Please enter a description for your form.");
      return;
    }
    setLoading(true);
    setError("");
    setOutput("");
    try {
      const response = await fetch(`${API_BASE_URL}/api/generate-schema`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, model }),
      });
      if (!response.ok) {
        const err = await response.json();
        setError(err.error || "Failed to generate schema.");
        setOutput("");
      } else {
        const text = await response.text();
        setOutput(text);
      }
    } catch (err) {
      setError("Network error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!output) return;
    navigator.clipboard.writeText(output);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleClear = () => {
    setPrompt("");
    setOutput("");
    setError("");
  };

  const handleDownload = () => {
    if (!output) return;
    let json, label;
    try {
      json = JSON.parse(output);
      label = json.label || json.formLabel || json.title || "form";
    } catch (e) {
      setError("Output is not valid JSON. Cannot download.");
      return;
    }
    // Sanitize label for filename
    const fileName = `${
      label
        .replace(/[^a-zA-Z0-9 _-]/g, "")
        .replace(/\s+/g, " ")
        .trim() || "form"
    }.json`;
    const blob = new Blob([output], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="container">
      <div className="header">
        <h1>🚀 AI Form Generator</h1>
        <p>Transform your ideas into structured JSON forms instantly</p>
      </div>
      <div className="main-content">
        <div className="input-section">
          <label htmlFor="promptInput">
            🎯 Describe your form requirements:
          </label>
          <textarea
            id="promptInput"
            className="prompt-input"
            placeholder="Example: Create a contact form with name, email, phone number, subject, and message fields. Make name and email required."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && e.ctrlKey) handleGenerate();
            }}
          />
        </div>
        <div className="input-section" style={{ marginTop: 20 }}>
          <label htmlFor="modelSelect">🤖 Select Model:</label>
          <div style={{ display: "flex", gap: 20, flexWrap: "wrap" }}>
            {models.map((opt) => (
              <label
                key={opt.value}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  cursor: "pointer",
                }}
              >
                <input
                  type="radio"
                  name="model"
                  value={opt.value}
                  checked={model === opt.value}
                  onChange={() => setModel(opt.value)}
                  style={{ marginRight: 6 }}
                />
                {opt.label}
              </label>
            ))}
          </div>
        </div>
        <div className="button-section">
          <button
            className="btn btn-primary"
            onClick={handleGenerate}
            disabled={loading}
          >
            ✨ Generate Form JSON
          </button>
          <button className="btn btn-secondary" onClick={handleClear}>
            🗑️ Clear All
          </button>
        </div>
        {loading && (
          <div className="loading show">
            <div className="spinner"></div>
            <span>Generating your form... Please wait</span>
          </div>
        )}
        {error && (
          <div className="error">
            <strong>Error:</strong> {error}
          </div>
        )}
        <div className="output-section">
          <div className="output-header">
            <h3>📄 Generated JSON Output:</h3>
          </div>
          <div className="output-container">
            <button
              className={`copy-button${copied ? " copied" : ""}`}
              onClick={handleCopy}
            >
              {copied ? "✓ Copied!" : "📋 Copy"}
            </button>
            <button
              className="download-button"
              onClick={handleDownload}
              style={{ marginLeft: 10 }}
            >
              ⬇️ Download JSON
            </button>
            <textarea
              className="output-text"
              value={output}
              placeholder="Your generated JSON will appear here..."
              readOnly
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
