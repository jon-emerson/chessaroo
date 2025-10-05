'use client';

import { useEffect, useState } from 'react';

export default function Footer() {
  const [deployTime, setDeployTime] = useState<string>('');

  useEffect(() => {
    const formatPacificTime = (value: string | number | Date) => {
      try {
        return new Date(value).toLocaleString('en-US', {
          timeZone: 'America/Los_Angeles',
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: 'numeric',
          minute: '2-digit',
          second: '2-digit',
          hour12: true,
        });
      } catch (error) {
        console.error('Failed to format deployment time:', error);
        return '';
      }
    };

    const setFormattedDeployTime = (value?: string) => {
      const formatted = formatPacificTime(value ?? Date.now());
      setDeployTime(formatted ? `${formatted} (PT)` : '');
    };

    fetch('/api/deployment-info')
      .then((response) => response.json())
      .then((data) => {
        if (data.deploymentTime) {
          setFormattedDeployTime(data.deploymentTime);
        } else {
          setFormattedDeployTime();
        }
      })
      .catch((error) => {
        console.error('Failed to fetch deployment info:', error);
        setFormattedDeployTime();
      });
  }, []);

  return (
    <footer className="border-t border-slate-800/80 bg-slate-950/60">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-6 py-10 sm:px-8 lg:px-10">
        <div className="flex flex-col gap-4 text-sm text-slate-400 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-base font-semibold text-slate-100">Sharpen your instincts.</p>
            <p>Every blunder has a fingerprint. BlunderLab surfaces it before your opponent does.</p>
          </div>
          <div className="rounded-2xl border border-slate-800/70 bg-slate-900/70 px-4 py-3 text-xs uppercase tracking-wide text-slate-400">
            {deployTime ? `Latest deploy: ${deployTime}` : 'Calibrating deployment clock…'}
          </div>
        </div>
        <div className="divider" />
        <div className="flex flex-col-reverse gap-3 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between">
          <p>© {new Date().getFullYear()} BlunderLab. Train hard. Blunder less.</p>
          <div className="flex items-center gap-3 text-slate-400">
            <span className="pill-muted">Dark Mode</span>
            <span className="pill-muted">Powered by chess.js</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
