export function getRiskTone(value) {
  if (value < 40) {
    return {
      level: 'Low',
      color: '#22c55e',
      caption: 'Low-exposure patterns dominate the current submission.',
    };
  }

  if (value < 70) {
    return {
      level: 'Medium',
      color: '#f59e0b',
      caption: 'Moderate issues detected. Review before shipping.',
    };
  }

  return {
    level: 'High',
    color: '#ef4444',
    caption: 'Elevated risk detected across multiple analysis signals.',
  };
}

export function getBugTone(value) {
  if (value <= 0) {
    return {
      level: 'Clean',
      color: '#22c55e',
      caption: 'No buggy lines were reported by the detector.',
    };
  }

  if (value < 20) {
    return {
      level: 'Low',
      color: '#22c55e',
      caption: 'A small portion of the code was flagged as buggy.',
    };
  }

  if (value < 50) {
    return {
      level: 'Medium',
      color: '#f59e0b',
      caption: 'Several lines were flagged. Review the findings before shipping.',
    };
  }

  return {
    level: 'High',
    color: '#ef4444',
    caption: 'A large portion of the submitted code was flagged as buggy.',
  };
}

export function calculateBugPercentage(analysis) {
  const codeLines = countSignificantLines(analysis.input_code || '');

  if (codeLines === 0) {
    return 0;
  }

  const bugLines = new Set(
    (analysis.bugs || [])
      .map((bug) => Number(bug.line))
      .filter((line) => Number.isInteger(line) && line > 0),
  );

  if (bugLines.size > 0) {
    return Math.min(100, (bugLines.size / codeLines) * 100);
  }

  return (analysis.bugs || []).length > 0 ? Math.min(100, 100 / codeLines) : 0;
}

export function buildAnalysisSummary(analysis) {
  const totals = {
    bugs: (analysis.bugs || []).length,
    security: (analysis.security || []).length,
    anomalies: (analysis.anomalies || []).length,
    dos: (analysis.dos_risk || []).length,
  };

  const totalSignals = totals.bugs + totals.security + totals.anomalies + totals.dos;
  const categories = Object.values(totals).filter((count) => count > 0).length;
  const level = analysis.risk?.level || 'UNKNOWN';
  const fixStatus = analysis.fixed_code?.status || 'idle';

  return {
    valueCaption: '',
    riskLevelBadge: level,
    signalCount: String(totalSignals),
    engineState: totalSignals > 0 ? 'Flagged' : 'Clear',
    categoryCount: String(categories),
    analysisState: totalSignals > 0 ? 'Complete' : 'Clean',
    fixStatusBadge: fixStatus.charAt(0).toUpperCase() + fixStatus.slice(1),
    riskBand: '',
  };
}

export function formatFindings(analysis) {
  const riskItems = [];
  const riskLevel = analysis.risk?.level;
  const riskPercent = analysis.risk?.percentage;
  const riskReasons = analysis.risk?.reasons || [];

  if (riskLevel) {
    const suffix = typeof riskPercent === 'number' ? ` (${riskPercent}%)` : '';
    riskItems.push(`- Level: ${riskLevel}${suffix}`);
  }
  riskItems.push(...riskReasons.map((reason) => `- ${reason}`));

  const errorItems = [];
  if (analysis.debug?.status === 'error') {
    errorItems.push(`- Runtime error: ${analysis.debug.message || 'Execution failed.'}`);
  } else if (analysis.debug?.status === 'skipped') {
    errorItems.push(`- Runtime check: ${analysis.debug.message || 'Skipped.'}`);
  }

  errorItems.push(
    ...(analysis.bugs || [])
      .filter((bug) => bug.type === 'tool_error')
      .map((bug) => `- Bug detector error: ${bug.message || 'Tool execution failed.'}`),
  );
  errorItems.push(
    ...(analysis.security || [])
      .filter((issue) => issue.type === 'tool_error')
      .map((issue) => `- Security analyzer error: ${issue.message || 'Tool execution failed.'}`),
  );

  const sections = [
    {
      title: 'Analysis Notes',
      items: (analysis.analysis_notes || []).map((note) => `- ${note}`),
    },
    {
      title: 'Risk Summary',
      items: riskItems,
    },
    {
      title: 'Errors',
      items: errorItems,
    },
    {
      title: 'Bug Warnings',
      items: (analysis.bugs || [])
        .filter((bug) => bug.type !== 'tool_error')
        .map((bug) => formatStructuredIssue(bug)),
    },
    {
      title: 'Security Issues',
      items: (analysis.security || [])
        .filter((issue) => issue.type !== 'tool_error')
        .map((issue) => formatStructuredIssue(issue)),
    },
    {
      title: 'Anomalies',
      items: (analysis.anomalies || []).map((issue) => formatStructuredIssue(issue)),
    },
    {
      title: 'DoS Risks',
      items: (analysis.dos_risk || []).map((issue) => `- ${issue}`),
    },
  ];

  const rendered = sections
    .filter((section) => section.items.length > 0)
    .map((section) => `${section.title}:\n${section.items.join('\n')}`);

  return rendered.length > 0
    ? rendered.join('\n\n')
    : 'No bugs or risky patterns were detected for this code.';
}

export function formatFixedCode(analysis) {
  const fixed = analysis.fixed_code;

  if (!fixed) {
    return 'No fixed code was returned by the backend.';
  }

  return removeRepeatedFullText(fixed.code || fixed.message || 'Fixed code is currently unavailable.');
}

function formatStructuredIssue(issue) {
  const message = issue.message || issue.type || 'Issue detected';
  const line = issue.line ? `Line ${issue.line}` : 'Line unknown';
  const detail = issue.symbol ? ` (${issue.symbol})` : '';
  return `- ${line}: ${message}${detail}`;
}

function countSignificantLines(code) {
  return code
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith('#'))
    .length;
}

function removeRepeatedFullText(text) {
  const normalized = text.replace(/\r\n/g, '\n').trim();
  const lines = normalized.split('\n');

  for (let splitIndex = 2; splitIndex < lines.length; splitIndex += 1) {
    const firstHalf = lines.slice(0, splitIndex).join('\n').trim();
    const secondHalf = lines.slice(splitIndex).join('\n').trim();

    if (firstHalf.length >= 30 && firstHalf === secondHalf) {
      return firstHalf;
    }
  }

  return normalized;
}
