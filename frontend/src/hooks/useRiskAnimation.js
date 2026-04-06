import { useEffect, useRef } from 'react';
import { easeInOut } from '../utils/animation.js';

export function useRiskAnimation(setRiskScore) {
  const animationFrameRef = useRef(null);

  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  function animateRisk({ end, start, duration = 1800 }) {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }

    let startTime = null;

    function animation(currentTime) {
      if (!startTime) startTime = currentTime;

      const progressTime = currentTime - startTime;
      const animationPercent = easeInOut(Math.min(progressTime / duration, 1));
      const value = start + (end - start) * animationPercent;

      setRiskScore(value);

      if (progressTime < duration) {
        animationFrameRef.current = requestAnimationFrame(animation);
      }
    }

    animationFrameRef.current = requestAnimationFrame(animation);
  }

  return animateRisk;
}
