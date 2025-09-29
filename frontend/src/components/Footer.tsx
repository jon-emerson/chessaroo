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
      .then(response => response.json())
      .then(data => {
        if (data.deploymentTime) {
          setFormattedDeployTime(data.deploymentTime);
        } else {
          setFormattedDeployTime();
        }
      })
      .catch(error => {
        console.error('Failed to fetch deployment info:', error);
        setFormattedDeployTime();
      });
  }, []);

  return (
    <footer className="mt-5 py-3 bg-light border-top">
      <div className="container">
        <div className="row">
          <div className="col-12 text-center">
            <small className="text-muted">
              {deployTime && (
                <>
                  Server deployed: {deployTime}
                </>
              )}
            </small>
          </div>
        </div>
      </div>
    </footer>
  );
}
