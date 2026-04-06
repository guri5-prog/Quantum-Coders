import BugPercentagePanel from './BugPercentagePanel.jsx';

function EditorPanel({ bugPercentage, bugTone, inputCode, isLoading, onAnalyze, onInputChange }) {
  return (
    <div className="panel editor-panel reveal">
      <div className="panel-header">
        <div>
          <p className="section-tag">Source Input</p>
          <h3>Code Submission</h3>
        </div>
        <span className="panel-badge">Ready</span>
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
