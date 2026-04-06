import { useRef } from 'react';

import BugPercentagePanel from './BugPercentagePanel.jsx';

const LANGUAGE_OPTIONS = [
  { value: 'python', label: 'Python' },
  { value: 'java', label: 'Java' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'cpp', label: 'C++' },
];

function EditorPanel({
  bugPercentage,
  bugTone,
  inputCode,
  isLoading,
  language,
  uploadedFileName,
  onAnalyze,
  onFileUpload,
  onInputChange,
  onLanguageChange,
}) {
  const fileInputRef = useRef(null);

  function handlePickFile() {
    fileInputRef.current?.click();
  }

  function handleFileChange(event) {
    const [file] = event.target.files || [];
    onFileUpload(file);
    event.target.value = '';
  }

  return (
    <div className="panel editor-panel reveal">
      <div className="panel-header">
        <div>
          <p className="section-tag">Source Input</p>
          <h3>Code Submission</h3>
        </div>
        <span className="panel-badge">Ready</span>
      </div>

      <div className="language-row">
        <label htmlFor="languageSelect">Language</label>
        <select
          id="languageSelect"
          className="language-select"
          value={language}
          onChange={(event) => onLanguageChange(event.target.value)}
          disabled={isLoading}
        >
          {LANGUAGE_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>

        <div className="upload-row">
          <input
            ref={fileInputRef}
            type="file"
            className="file-input-hidden"
            onChange={handleFileChange}
            disabled={isLoading}
          />
          <button
            type="button"
            className="buttons secondary-button upload-button"
            onClick={handlePickFile}
            disabled={isLoading}
          >
            Upload File
          </button>
          <p className="upload-hint">
            {uploadedFileName
              ? `Loaded: ${uploadedFileName}`
              : `Choose a ${LANGUAGE_OPTIONS.find((option) => option.value === language)?.label || 'code'} file.`}
          </p>
        </div>
      </div>

      <label htmlFor="inputCode">Enter your code below for analysis</label>
      <div className="editor-frame">
        <div className="editor-toolbar">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <textarea
          rows="14"
          id="inputCode"
          placeholder="# Your code goes here..."
          spellCheck="false"
          value={inputCode}
          onChange={(event) => onInputChange(event.target.value)}
        ></textarea>
      </div>

      <button type="button" className="buttons primary-button" disabled={isLoading} onClick={onAnalyze}>
        <span className="button-shine"></span>
        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path>
        </svg>
        <span>{isLoading ? 'Analyzing...' : 'Analyze Code'}</span>
      </button>

      <BugPercentagePanel
        bugPercentage={bugPercentage}
        isLoading={isLoading}
        tone={bugTone}
      />
    </div>
  );
}

export default EditorPanel;
