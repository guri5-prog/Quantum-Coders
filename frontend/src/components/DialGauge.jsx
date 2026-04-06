function DialGauge({ caption, className = '', color, dashOffset, label, needleAngle, value }) {
  return (
    <div className={`dial-container ${className}`.trim()}>
      <svg className="dial" width="240" height="150" viewBox="0 0 200 120" aria-hidden="true">
        <path
          className="dial-bg-circle"
          d="M20 100 A80 80 0 0 1 180 100"
          strokeWidth="12"
          fill="none"
          strokeLinecap="round"
        />

        <path
          className="dial-progress"
          d="M20 100 A80 80 0 0 1 180 100"
          strokeWidth="12"
          fill="none"
          pathLength="100"
          strokeDasharray="100"
          strokeDashoffset={dashOffset}
          strokeLinecap="round"
          style={{ stroke: color }}
        />

        <line
          className="dial-needle"
          x1="100"
          y1="100"
          x2="100"
          y2="25"
          strokeWidth="4"
          style={{ transform: `rotate(${needleAngle}deg)`, stroke: color }}
        />

        <circle cx="100" cy="100" r="6" className="dial-center" />
      </svg>
      <div className="value-stack">
        <div className="value-text">{label}: {value}</div>
        <p className="value-caption">{caption}</p>
      </div>
    </div>
  );
}

export default DialGauge;
