import DialGauge from './DialGauge.jsx';

function ScorePanel({ dashOffset, isLoading, needleAngle, riskBand, riskScore, summary, tone, valueCaption }) {
  return (
    <section className="panel score-panel reveal">
      <div className="panel-header">
        <div>
          <p className="section-tag">Risk Index</p>
          <h3>Threat Dial</h3>
        </div>
        <span className="panel-badge">{summary.riskLevelBadge}</span>
      </div>

      <DialGauge
        caption={valueCaption}
        color={tone.color}
        dashOffset={dashOffset}
        label="Risk Score"
        needleAngle={needleAngle}
        value={isLoading ? '...' : Math.round(riskScore)}
      />

      <div className="mini-stats">
        <article className="stat-card">
          <span className="stat-label">Risk band</span>
          <strong>{riskBand}</strong>
        </article>
        <article className="stat-card">
          <span className="stat-label">Signals found</span>
          <strong>{summary.signalCount}</strong>
        </article>
        <article className="stat-card">
          <span className="stat-label">Engine state</span>
          <strong>{summary.engineState}</strong>
        </article>
      </div>
    </section>
  );
}

export default ScorePanel;
