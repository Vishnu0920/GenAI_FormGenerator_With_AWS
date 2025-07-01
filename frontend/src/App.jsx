import React, { useState } from 'react';
import './App.css';

const API_BASE_URL = 'http://localhost:5000';

function App() {
  const [prompt, setPrompt] = useState('');
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a description for your form.');
      return;
    }
    setLoading(true);
    setError('');
    setOutput('');
    try {
      const response = await fetch(`${API_BASE_URL}/api/generate-schema`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      });
      if (!response.ok) {
        const err = await response.json();
        setError(err.error || 'Failed to generate schema.');
        setOutput('');
      } else {
        const text = await response.text();
        setOutput(text);
      }
    } catch (err) {
      setError('Network error: ' + err.message);
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
    setPrompt('');
    setOutput('');
    setError('');
  };

  return (
    <div className="container">
      <div className="header">
        <h1>🚀 AI Form Generator</h1>
        <p>Transform your ideas into structured JSON forms instantly</p>
      </div>
      <div className="main-content">
        <div className="input-section">
          <label htmlFor="promptInput">🎯 Describe your form requirements:</label>
          <textarea
            id="promptInput"
            className="prompt-input"
            placeholder="Example: Create a contact form with name, email, phone number, subject, and message fields. Make name and email required."
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter' && e.ctrlKey) handleGenerate();
            }}
          />
        </div>
        <div className="button-section">
          <button className="btn btn-primary" onClick={handleGenerate} disabled={loading}>
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
              className={`copy-button${copied ? ' copied' : ''}`}
              onClick={handleCopy}
            >
              {copied ? '✓ Copied!' : '📋 Copy'}
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
