function Header({ onToggleTheme }) {
  return (
    <header className="topbar reveal">
      <div>
        <p className="eyebrow">Predictive security diagnostics</p>
        <h1 id="title">Bug Analyzer</h1>
      </div>
      <div className="topbar-actions">
        <div className="status-pill">
          <span className="status-dot"></span>
          <span>Live analysis pipeline</span>
        </div>
        <button type="button" className="buttons secondary-button" onClick={onToggleTheme}>
          Toggle Theme
        </button>
      </div>
    </header>
  );
}

export default Header;
