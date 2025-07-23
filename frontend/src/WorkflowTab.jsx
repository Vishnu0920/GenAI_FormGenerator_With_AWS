import React, { useState } from "react";

const API_BASE_URL = "http://localhost:5000";

function WorkflowTab({ models }) {
  const [prompt, setPrompt] = useState("");
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const [model, setModel] = useState(models.length > 0 ? models[0].value : "");
  const [jsonSize, setJsonSize] = useState(0);

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError("Please enter a description for your workflow.");
      return;
    }
    setLoading(true);
    setError("");
    setOutput("");
    setJsonSize(0);
    try {
      const response = await fetch(`${API_BASE_URL}/api/generate-workflow`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, model }),
      });
      if (!response.ok) {
        const err = await response.json();
        setError(err.error || "Failed to generate workflow.");
        setOutput("");
        setJsonSize(0);
      } else {
        const text = await response.text();
        setOutput(text);
        setJsonSize(new Blob([text]).size);
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
    setJsonSize(0);
  };
  const handleDownload = () => {
    if (!output) return;
    if (jsonSize > 400 * 1024) {
      setError("File size exceeds 400kB limit. Cannot download.");
      return;
    }
    let json, label;
    try {
      json = JSON.parse(output);
      label = json.label || json.workflowLabel || json.title || "workflow";
    } catch (e) {
      setError("Output is not valid JSON. Cannot download.");
      return;
    }
    const fileName = `${
      label
        .replace(/[^a-zA-Z0-9 _-]/g, "")
        .replace(/\s+/g, " ")
        .trim() || "workflow"
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
    <div className="main-content">
      <div className="input-section">
        <label htmlFor="workflowPromptInput">
          🛠️ Describe your workflow requirements:
        </label>
        <textarea
          id="workflowPromptInput"
          className="prompt-input"
          placeholder="Example: Create a workflow for onboarding a new employee with steps for document submission, manager approval, and IT setup."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && e.ctrlKey) handleGenerate();
          }}
        />
      </div>
      <div className="input-section" style={{ marginTop: 20 }}>
        <label htmlFor="workflowModelSelect">🤖 Select Model:</label>
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
                name="workflowModel"
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
          ✨ Generate Workflow JSON
        </button>
        <button className="btn btn-secondary" onClick={handleClear}>
          🗑️ Clear All
        </button>
      </div>
      {loading && (
        <div className="loading show">
          <div className="spinner"></div>
          <span>Generating your workflow... Please wait</span>
        </div>
      )}
      {error && (
        <div className="error">
          <strong>Error:</strong> {error}
        </div>
      )}
      <div className="output-section">
        <div className="output-header minimal-output-header">
          <h3>Generated JSON</h3>
          {output && (
            <span className="json-size">
              Size: {(jsonSize / 1024).toFixed(1)} kB
            </span>
          )}
        </div>
        <div className="output-container">
          <div className="button-group">
            <button
              className={`copy-button minimal-copy${copied ? " copied" : ""}`}
              onClick={handleCopy}
            >
              {copied ? "✓ Copied" : "📋 Copy"}
            </button>
            <button
              className="download-button minimal-download"
              onClick={handleDownload}
              disabled={jsonSize > 400 * 1024}
              title={
                jsonSize > 400 * 1024
                  ? "File too large to download"
                  : "Download JSON"
              }
            >
              💾 Download
            </button>
          </div>
          <textarea
            className="output-text"
            value={output}
            placeholder="Your generated workflow JSON will appear here..."
            readOnly
          />
        </div>
      </div>
    </div>
  );
}

export default WorkflowTab;
