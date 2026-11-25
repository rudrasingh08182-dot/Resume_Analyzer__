import React, { useState } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Handle file selection
  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    if (!selectedFile) return;

    const allowedTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ];

    if (!allowedTypes.includes(selectedFile.type)) {
      setError("Please upload only PDF or DOCX files.");
      setFile(null);
      setResult(null);
      return;
    }

    setFile(selectedFile);
    setError("");
    setResult(null);
  };

  // Upload resume to backend
  const handleAnalyze = async () => {
    if (!file) {
      setError("Please select a resume first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/upload-resume", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Resume analysis failed.");
      }

      setResult(data);
    } catch (err) {
      setError(err.message || "Unable to connect to the backend.");
    } finally {
      setLoading(false);
    }
  };

  // Reset the page
  const handleReset = () => {
    setFile(null);
    setResult(null);
    setError("");
  };

  return (
    <div className="app">
      <header className="header">
        <h1>Resume Analyzer</h1>
        <p>AI-powered resume analysis</p>
      </header>

      <main className="container">
        <section className="upload-section">
          <h2>Analyze Your Resume</h2>
          <p>
            Upload your resume to identify your job category and technical skills.
          </p>

          <div className="upload-box">
            <input
              type="file"
              accept=".pdf,.docx"
              onChange={handleFileChange}
            />

            {file && (
              <p className="file-name">
                Selected file: {file.name}
              </p>
            )}
          </div>

          <button
            className="analyze-btn"
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? "Analyzing..." : "Analyze Resume"}
          </button>

          {error && <p className="error-message">{error}</p>}
        </section>

        {result && (
          <section className="results-section">
            <h2>Analysis Results</h2>

            <div className="result-card">
              <h3>Predicted Category</h3>
              <p>{result.predicted_category}</p>
            </div>

            <div className="result-card">
              <h3>Confidence</h3>
              <p>{result.confidence}%</p>
            </div>

            <div className="result-card">
              <h3>Total Skills Detected</h3>
              <p>{result.total_skills}</p>
            </div>

            <div className="skills-section">
              <h3>Detected Skills</h3>

              <div className="skills-list">
                {result.skills.map((skill, index) => (
                  <span className="skill-tag" key={index}>
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            <button className="reset-btn" onClick={handleReset}>
              Analyze Another Resume
            </button>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;