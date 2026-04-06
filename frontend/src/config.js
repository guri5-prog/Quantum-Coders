export const API_URL = localStorage.getItem('bugAnalyzerApiUrl') || 'http://127.0.0.1:8000/analyze';

export const initialSummary = {
  bugOutput: '',
  fixedCodeOutput: '',
  valueCaption: 'Waiting for analysis input.',
  riskLevelBadge: 'Idle',
  signalCount: '0',
  engineState: 'Standby',
  categoryCount: '0',
  analysisState: 'Idle',
  fixStatusBadge: 'Idle',
  riskBand: '',
};

export const loadingSummary = {
  bugOutput: 'Analyzing code and collecting findings...',
  fixedCodeOutput: 'Generating safer replacement code...',
  valueCaption: 'Running parser, detectors, and scoring engine.',
  riskLevelBadge: 'Running',
  engineState: 'Scanning',
  analysisState: 'Processing',
  fixStatusBadge: 'Generating',
};
