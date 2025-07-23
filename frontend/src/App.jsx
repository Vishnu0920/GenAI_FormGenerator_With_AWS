import React, { useState, useEffect } from "react";
import "./App.css";
import WorkflowTab from "./WorkflowTab";

const API_BASE_URL = "http://localhost:5000";

function App() {
  const [models, setModels] = useState([]);
  const [tab, setTab] = useState("form");

  // Form tab state
  const [prompt, setPrompt] = useState("");
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const [model, setModel] = useState("");

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/models`)
      .then((res) => res.json())
      .then((data) => {
        setModels(data);
        if (data.length > 0) setModel(data[0].value);
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
        <h1>🚀 AI Generator</h1>
        <p>
          Transform your ideas into structured JSON for forms and workflows
          instantly
        </p>
      </div>
      <div
        style={{
          display: "flex",
          borderBottom: "2px solid #e0e0e0",
          background: "#f8f9fa",
        }}
      >
        <button
          className={"tab-btn" + (tab === "form" ? " active" : "")}
          onClick={() => setTab("form")}
          style={{
            flex: 1,
            padding: 18,
            border: "none",
            background: tab === "form" ? "#fff" : "#f8f9fa",
            fontWeight: 600,
            fontSize: 18,
            color: tab === "form" ? "#4caf50" : "#333",
            borderBottom:
              tab === "form" ? "2px solid #4caf50" : "2px solid transparent",
            cursor: "pointer",
            transition: "all 0.2s",
          }}
        >
          Form Generator
        </button>
        <button
          className={"tab-btn" + (tab === "workflow" ? " active" : "")}
          onClick={() => setTab("workflow")}
          style={{
            flex: 1,
            padding: 18,
            border: "none",
            background: tab === "workflow" ? "#fff" : "#f8f9fa",
            fontWeight: 600,
            fontSize: 18,
            color: tab === "workflow" ? "#4caf50" : "#333",
            borderBottom:
              tab === "workflow"
                ? "2px solid #4caf50"
                : "2px solid transparent",
            cursor: "pointer",
            transition: "all 0.2s",
          }}
        >
          Workflow Generator
        </button>
      </div>
      {tab === "form" ? (
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
              <div className="button-group">
                <button
                  className={`copy-button minimal-copy${
                    copied ? " copied" : ""
                  }`}
                  onClick={handleCopy}
                >
                  {copied ? "✓ Copied" : "📋 Copy"}
                </button>
                <button
                  className="download-button minimal-download"
                  onClick={handleDownload}
                  disabled={false}
                  title="Download JSON"
                >
                  💾 Download
                </button>
              </div>
              <textarea
                className="output-text"
                value={output}
                placeholder="Your generated JSON will appear here..."
                readOnly
              />
            </div>
          </div>
        </div>
      ) : (
        <WorkflowTab models={models} />
      )}
    </div>
  );
}

export default App;
