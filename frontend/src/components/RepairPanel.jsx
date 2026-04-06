function RepairPanel({ summary }) {
  return (
    <section className="panel findings-panel reveal">
      <div className="panel-header">
        <div>
          <p className="section-tag">Repair Output</p>
          <h3>Fixed Code</h3>
        </div>
        <span className="panel-badge">{summary.fixStatusBadge}</span>
      </div>

      <textarea value={summary.fixedCodeOutput} readOnly placeholder="Generated fixed code will appear here..."></textarea>
    </section>
  );
}

export default RepairPanel;
