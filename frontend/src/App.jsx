import { useRef, useState } from 'react';
import EditorPanel from './components/EditorPanel.jsx';
import FindingsPanel from './components/FindingsPanel.jsx';
import Header from './components/Header.jsx';
import Hero from './components/Hero.jsx';
import RepairPanel from './components/RepairPanel.jsx';
import ScorePanel from './components/ScorePanel.jsx';
import { API_URL, initialSummary, loadingSummary } from './config.js';
import { useBodyState } from './hooks/useBodyState.js';
import { useRiskAnimation } from './hooks/useRiskAnimation.js';
import { requestAnalysis } from './services/analyzeApi.js';
import {
  buildAnalysisSummary,
  calculateBugPercentage,
  formatFindings,
  formatFixedCode,
  getBugTone,
  getRiskTone,
} from './utils/analysis.js';

function App() {
  const [inputCode, setInputCode] = useState('');
  const [isDark, setIsDark] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [bugPercentage, setBugPercentage] = useState(0);
  const [riskScore, setRiskScore] = useState(0);
  const [summary, setSummary] = useState(initialSummary);
  const currentBugPercentageRef = useRef(0);
  const currentRiskRef = useRef(0);
  const animateBugPercentage = useRiskAnimation(setBugPercentage);
  const animateRisk = useRiskAnimation(setRiskScore);

  const bugTone = getBugTone(bugPercentage);
  const tone = getRiskTone(riskScore);
  const valueCaption = isLoading
    ? loadingSummary.valueCaption
    : summary.valueCaption || tone.caption;
  const riskBand = summary.riskBand || tone.level;
  const percent = Math.max(0, Math.min(1, riskScore / 100));
  const needleAngle = percent * 180 - 90;
  const dashOffset = 100 - (100 * percent);

  useBodyState({ isDark, isLoading, riskLevel: tone.level });

  async function handleAnalyze(event) {
    event.preventDefault();
    const userCode = inputCode.trim();

    if (!userCode) {
      setSummary((current) => ({
        ...current,
        bugOutput: 'Paste code before starting analysis.',
        valueCaption: 'Submission blocked until source input is provided.',
      }));
      return;
    }

    setIsLoading(true);
    setSummary((current) => ({ ...current, ...loadingSummary }));

    try {
      const analysis = await requestAnalysis(userCode);
      const riskValue = analysis.risk.percentage;
      const bugPercentageValue = calculateBugPercentage(analysis);

      animateBugPercentage({ end: bugPercentageValue, start: currentBugPercentageRef.current });
      animateRisk({ end: riskValue, start: currentRiskRef.current });

      currentBugPercentageRef.current = bugPercentageValue;
      currentRiskRef.current = riskValue;
      setSummary({
        ...buildAnalysisSummary(analysis),
        bugOutput: formatFindings(analysis),
        fixedCodeOutput: formatFixedCode(analysis),
      });
    } catch (error) {
      handleAnalysisError(error);
    } finally {
      setIsLoading(false);
    }
  }

  function handleAnalysisError(error) {
    const friendlyMessage = error.message === 'Failed to fetch'
      ? `Could not reach the backend at ${API_URL}. Make sure the FastAPI server is running.`
      : (error.message || 'Submission failed or backend not running.');

    alert(friendlyMessage);
    currentBugPercentageRef.current = 0;
    currentRiskRef.current = 0;
    setBugPercentage(0);
    setRiskScore(0);
    setSummary({
      bugOutput: `Request failed.\nEndpoint: ${API_URL}\nReason: ${friendlyMessage}`,
      fixedCodeOutput: 'Fixed code could not be generated because the analysis request failed.',
      valueCaption: 'Analysis failed before a valid response was returned.',
      riskLevelBadge: 'Error',
      signalCount: '0',
      engineState: 'Offline',
      categoryCount: '0',
      analysisState: 'Failed',
      fixStatusBadge: 'Unavailable',
      riskBand: 'Unavailable',
    });
  }

  return (
    <>
      <BackgroundEffects />

      <div className="page-shell">
        <Header onToggleTheme={() => setIsDark((value) => !value)} />

        <main className="dashboard">
          <Hero />

          <section className="workspace">
            <EditorPanel
              bugPercentage={bugPercentage}
              bugTone={bugTone}
              inputCode={inputCode}
              isLoading={isLoading}
              onAnalyze={handleAnalyze}
              onInputChange={setInputCode}
            />

            <div className="results-column">
              <ScorePanel
                dashOffset={dashOffset}
                isLoading={isLoading}
                needleAngle={needleAngle}
                riskBand={riskBand}
                riskScore={riskScore}
                summary={summary}
                tone={tone}
                valueCaption={valueCaption}
              />
              <FindingsPanel summary={summary} />
              <RepairPanel summary={summary} />
            </div>
          </section>
        </main>

        <footer className="copyright">2026 Bug Analyzer. Built for secure code.</footer>
      </div>
    </>
  );
}

function BackgroundEffects() {
  return (
    <>
      <div className="ambient ambient-one"></div>
      <div className="ambient ambient-two"></div>
      <div className="grid-glow"></div>
    </>
  );
}

export default App;
