function FindingsPanel({ summary }) {
  return (
    <section className="panel findings-panel reveal">
      <div className="panel-header">
        <div>
          <p className="section-tag">Detection Summary</p>
          <h3>Detected Findings</h3>
        </div>
        <span className="panel-badge">Structured</span>
      </div>

      <div className="findings-meta">
        <div className="meta-card">
          <span>Total categories</span>
          <strong>{summary.categoryCount}</strong>
        </div>
        <div className="meta-card">
          <span>Current mode</span>
          <strong>{summary.analysisState}</strong>
        </div>
      </div>

      <textarea value={summary.bugOutput} readOnly placeholder="Detailed breakdown of detected issues will appear here..."></textarea>
    </section>
  );
}

export default FindingsPanel;
