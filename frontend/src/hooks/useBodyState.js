import { useEffect } from 'react';

export function useBodyState({ isDark, isLoading, riskLevel }) {
  useEffect(() => {
    document.body.id = 'main';
    document.body.classList.toggle('dark', isDark);
    document.body.classList.toggle('is-loading', isLoading);
    document.body.dataset.risk = riskLevel.toLowerCase();

    return () => {
      document.body.classList.remove('dark', 'is-loading');
      delete document.body.dataset.risk;
      document.body.removeAttribute('id');
    };
  }, [isDark, isLoading, riskLevel]);
}
