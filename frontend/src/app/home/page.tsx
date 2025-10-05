'use client';

import { FormEvent, useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { apiCall } from '../../lib/api';
import { useAuth } from '../../contexts/AuthContext';

interface Game {
  id: number;
  title: string;
  user_color: string;
  opponent_name: string;
  status: string;
  result: string;
  created_at: string;
}

export default function HomeDashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading } = useAuth();
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [importUrl, setImportUrl] = useState('');
  const [importing, setImporting] = useState(false);
  const [importStatus, setImportStatus] = useState<string | null>(null);

  useEffect(() => {
    if (isLoading) {
      return;
    }

    if (!isAuthenticated) {
      setLoading(false);
      router.replace('/login');
      return;
    }

    const load = async () => {
      setLoading(true);
      await fetchGames();
    };

    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, isLoading]);

  const fetchGames = async () => {
    try {
      const response = await apiCall('/api/games');
      setError(null);
      setGames(response.games || []);
      setLoading(false);
    } catch (err) {
      setError('Failed to load games');
      setLoading(false);
    }
  };

  const handleImport = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setImportStatus(null);

    if (!importUrl.trim()) {
      setImportStatus('Please enter a Chess.com game URL.');
      return;
    }

    setImporting(true);
    try {
      const response = await apiCall('/api/imported-games', {
        method: 'POST',
        body: JSON.stringify({ url: importUrl.trim() }),
      });

      setImportUrl('');
      fetchGames();
      if (response?.importedGameId) {
        router.push(`/imported_game/${response.importedGameId}`);
        return;
      }
      setImportStatus('Game imported successfully.');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to import game.';
      setImportStatus(message);
    } finally {
      setImporting(false);
    }
  };

  const createSampleGame = async () => {
    try {
      const response = await apiCall('/api/create-sample-game');
      if (response.gameId) {
        router.push(`/game/${response.gameId}`);
      }
    } catch (err) {
      alert('Failed to create sample game');
    }
  };

  if (isLoading || loading) {
    return (
      <div className="loading-spinner">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="space-y-12">
      <div className="flex flex-wrap items-center justify-between gap-6">
        <div>
          <span className="pill-muted">Game intelligence dashboard</span>
          <h1 className="mt-3">Welcome back{user ? `, ${user.username}` : ''}</h1>
          <p className="mt-3 max-w-2xl text-base text-slate-300">
            Import a fresh game, detect repeatable mistakes in minutes, and launch a targeted training
            sprint before your next pairing.
          </p>
        </div>
        <button onClick={createSampleGame} className="btn-secondary whitespace-nowrap">
          Generate sample game
        </button>
      </div>

      <section className="surface-card space-y-6">
        <div className="space-y-2">
          <h2 className="text-xl font-semibold text-white">Import a Chess.com game</h2>
          <p className="text-sm text-slate-400">
            Paste a game link such as https://www.chess.com/game/live/143645010490. We store the raw payload
            so the analysis engine can flag recurring tactical traps and vulnerable openings.
          </p>
        </div>
        <form onSubmit={handleImport} className="grid gap-3 sm:grid-cols-[minmax(0,1fr)_auto]">
          <input
            type="url"
            className="input-field"
            placeholder="https://www.chess.com/game/live/123456789"
            value={importUrl}
            onChange={(event) => setImportUrl(event.target.value)}
            disabled={importing}
            required
          />
          <button type="submit" className="btn-primary" disabled={importing}>
            {importing ? 'Importing…' : 'Import game'}
          </button>
        </form>
        {importStatus && <p className="text-sm text-slate-400">{importStatus}</p>}
      </section>

      <section className="space-y-6">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-xl font-semibold text-white">Recent games</h2>
          <span className="pill-muted">Last 10 imports</span>
        </div>

        {error && (
          <div className="rounded-2xl border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
            {error}
          </div>
        )}

        {games.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {games.map((game) => (
              <Link
                key={game.id}
                href={`/game/${game.id}`}
                className="surface-card group flex h-full flex-col gap-4 transition hover:border-cyan-500/40 hover:shadow-glow"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-500">{game.status}</p>
                    <h3 className="mt-1 text-lg font-semibold text-white">{game.title}</h3>
                  </div>
                  <span className="pill-muted">{new Date(game.created_at).toLocaleDateString()}</span>
                </div>
                <p className="text-sm text-slate-300">
                  {game.user_color === 'w' ? (
                    <span>
                      <span className="text-white">{user?.username} (White)</span> vs{' '}
                      <span className="text-white">{game.opponent_name || 'Anonymous'}</span>
                    </span>
                  ) : (
                    <span>
                      <span className="text-white">{game.opponent_name || 'Anonymous'}</span> vs{' '}
                      <span className="text-white">{user?.username} (Black)</span>
                    </span>
                  )}
                </p>
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span className="uppercase tracking-wide">Imported {new Date(game.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  {game.result !== '*' && <span className="badge-soft-primary">Result {game.result}</span>}
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="surface-card space-y-3 text-sm text-slate-300">
            <h3 className="text-lg font-semibold text-white">No games imported yet</h3>
            <p>
              Start by importing a game URL from Chess.com. We&apos;ll analyze it and surface the key tactics
              to drill.
            </p>
          </div>
        )}
      </section>
    </div>
  );
}
