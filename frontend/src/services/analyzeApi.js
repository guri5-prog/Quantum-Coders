import { API_URL } from '../config.js';

export async function requestAnalysis(code, language) {
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ code, language }),
  });

  if (!response.ok) {
    throw new Error(`Backend request failed with status ${response.status}`);
  }

  const result = await response.json();
  const analysis = result.results?.[0];
  const riskValue = analysis?.risk?.percentage;

  if (typeof riskValue !== 'number') {
    throw new Error(result.error || 'Backend returned an unexpected response.');
  }

  return analysis;
}
