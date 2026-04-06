import DialGauge from './DialGauge.jsx';

function BugPercentagePanel({ bugPercentage, isLoading, tone }) {
  const percent = Math.max(0, Math.min(1, bugPercentage / 100));
  const needleAngle = percent * 180 - 90;
  const dashOffset = 100 - (100 * percent);

  return (
    <section className="bug-percentage-card">
      <div className="bug-percentage-header">
        <div>
          <p className="section-tag">Bug Percentage</p>
          <h3>Buggy Code Dial</h3>
        </div>
        <span className="panel-badge">{tone.level}</span>
      </div>

      <DialGauge
        caption={isLoading ? 'Estimating buggy lines from detected issues.' : tone.caption}
        className="compact-dial"
        color={tone.color}
        dashOffset={dashOffset}
        label="Buggy Code"
        needleAngle={needleAngle}
        value={isLoading ? '...' : `${Math.round(bugPercentage)}%`}
      />
    </section>
  );
}

export default BugPercentagePanel;
