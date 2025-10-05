'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { apiCall } from '../../../lib/api';

interface ImportedGameDetails {
  id: number;
  chessComGameId: string;
  sourceUrl: string;
  whiteUsername: string | null;
  blackUsername: string | null;
  resultMessage: string | null;
  isFinished: boolean | null;
  gameEndReason: string | null;
  endTime: string | null;
  timeControl: string | null;
  importedAt: string | null;
  uuid: string | null;
}

export default function ImportedGamePage() {
  const params = useParams();
  const router = useRouter();
  const importedGameId = params.id as string;
  const [details, setDetails] = useState<ImportedGameDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (importedGameId) {
      fetchDetails();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [importedGameId]);

  const fetchDetails = async () => {
    try {
      const response = await apiCall(`/api/imported-games/${importedGameId}`);
      setDetails(response);
      setLoading(false);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unable to load imported game.';
      setError(message);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="flex flex-col items-center gap-4 text-center">
          <span className="h-12 w-12 animate-spin rounded-full border-2 border-slate-700/80 border-t-cyan-400" />
          <p className="text-sm text-slate-400">Retrieving import details…</p>
        </div>
      </div>
    );
  }

  if (error || !details) {
    return (
      <div className="surface-card space-y-4 text-sm text-slate-300">
        <h2 className="text-xl font-semibold text-white">Import not found</h2>
        <p>{error || 'We could not find that imported game.'}</p>
        <button onClick={() => router.push('/home')} className="btn-secondary w-max">
          ← Back to dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <button onClick={() => router.push('/home')} className="btn-secondary">
        ← Back to dashboard
      </button>

      <section className="surface-card space-y-8">
        <header className="space-y-2">
          <span className="pill-muted">Imported game</span>
          <h1 className="text-3xl font-semibold text-white">Chess.com import #{details.chessComGameId}</h1>
          <p className="text-sm text-slate-400">
            We keep the raw PGN so the mistake profiler can benchmark this game against your entire archive.
          </p>
        </header>

        <div className="grid gap-6 lg:grid-cols-2">
          <div className="surface-card bg-slate-900/70 p-6">
            <h3 className="text-lg font-semibold text-white">Players</h3>
            <dl className="mt-4 space-y-2 text-sm text-slate-300">
              <div className="flex items-center justify-between">
                <dt className="text-slate-400">White</dt>
                <dd className="font-medium text-white">{details.whiteUsername || 'Unknown'}</dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="text-slate-400">Black</dt>
                <dd className="font-medium text-white">{details.blackUsername || 'Unknown'}</dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="text-slate-400">Result</dt>
                <dd className="badge-soft-primary">
                  {details.resultMessage || (details.isFinished ? 'Completed' : 'Pending')}
                </dd>
              </div>
              {details.gameEndReason && (
                <div className="flex items-center justify-between">
                  <dt className="text-slate-400">End reason</dt>
                  <dd>{details.gameEndReason}</dd>
                </div>
              )}
            </dl>
          </div>

          <div className="surface-card bg-slate-900/70 p-6">
            <h3 className="text-lg font-semibold text-white">Metadata</h3>
            <dl className="mt-4 space-y-2 text-sm text-slate-300">
              <div className="flex items-center justify-between">
                <dt className="text-slate-400">Imported</dt>
                <dd>{details.importedAt ? new Date(details.importedAt).toLocaleString() : '—'}</dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="text-slate-400">Finished</dt>
                <dd>{details.endTime ? new Date(details.endTime).toLocaleString() : '—'}</dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="text-slate-400">Time control</dt>
                <dd>{details.timeControl || '—'}</dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="text-slate-400">Chess.com UUID</dt>
                <dd>{details.uuid || '—'}</dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="text-slate-400">Source</dt>
                <dd>
                  <a
                    href={details.sourceUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-cyan-300 hover:text-cyan-200"
                  >
                    View on Chess.com
                  </a>
                </dd>
              </div>
            </dl>
          </div>
        </div>

        <div className="surface-card-xl space-y-4 bg-slate-900/70">
          <h3 className="text-xl font-semibold text-white">Analysis pipeline</h3>
          <p className="text-sm text-slate-300">
            This import is queued for BlunderLab&apos;s mistake profiler. We examine the PGN for repeated
            tactical themes and weak opening responses across all of your stored games, then surface concise
            drills to prioritise in your next training block.
          </p>
          <ul className="list-disc space-y-2 pl-5 text-sm text-slate-300">
            <li>Fingerprint tactical traps that succeed against you—pins, skewers, forks, opposition squeezes.</li>
            <li>Cluster openings to highlight move numbers where your score collapses compared to masters.</li>
            <li>Recommend concrete alternative lines and prep a drill pack sized for a five-day sprint.</li>
          </ul>
          <p className="text-sm text-slate-400">
            Insights appear on your dashboard once background analysis completes. Re-import a game any time to
            refresh the metrics with your latest play.
          </p>
        </div>
      </section>
    </div>
  );
}
