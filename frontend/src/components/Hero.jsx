function Hero() {
  return (
    <section className="hero-card reveal">
      <div className="hero-copy">
        <p className="section-tag">Analysis Workspace</p>
        <h2>Inspect code with a more readable, animated risk surface.</h2>
        <p className="hero-text">
          Paste source code, run analysis, and inspect risk signals through motion-driven feedback and clearer findings.
        </p>
        <div className="hero-metrics">
          <div className="metric-chip">
            <span className="metric-label">Latency target</span>
            <strong>&lt; 2s UI response</strong>
          </div>
          <div className="metric-chip">
            <span className="metric-label">Output modes</span>
            <strong>Risk, bugs, security</strong>
          </div>
        </div>
      </div>
      <div className="hero-orbital">
        <div className="orbital-ring ring-one"></div>
        <div className="orbital-ring ring-two"></div>
        <div className="hero-core">
          <span>AI</span>
        </div>
      </div>
    </section>
  );
}

export default Hero;
