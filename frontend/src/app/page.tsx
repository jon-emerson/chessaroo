'use client';

import { useState, useEffect, FormEvent } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { apiCall } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

interface Game {
  id: number;
  title: string;
  user_color: string;
  opponent_name: string;
  status: string;
  result: string;
  created_at: string;
}

export default function HomePage() {
  const router = useRouter();
  const { user } = useAuth();
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [importUrl, setImportUrl] = useState('');
  const [importing, setImporting] = useState(false);
  const [importStatus, setImportStatus] = useState<string | null>(null);

  useEffect(() => {
    fetchGames();
  }, []);

  const fetchGames = async () => {
    try {
      const response = await apiCall('/api/games');
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
      const response = await apiCall('/api/imported-games/chesscom', {
        method: 'POST',
        body: JSON.stringify({ url: importUrl.trim() }),
      });

      setImportUrl('');
      fetchGames();
      if (response?.importedGameId) {
        router.push(`/imported_game/${response.importedGameId}`);
        return;
      } else {
        setImportStatus('Game imported successfully.');
      }
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
        // Navigate to the new game
        router.push(`/game/${response.gameId}`);
      }
    } catch (err) {
      alert('Failed to create sample game');
    }
  };

  if (loading) {
    return (
      <div className="loading-spinner">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="row">
      <div className="col-12">
        <h1>♕ Welcome to Chessaroo</h1>
        <p className="lead">A multiplayer chess application with real-time collaboration</p>
      </div>

      <div className="col-12">
        <div className="card mb-4">
          <div className="card-body">
            <h3 className="card-title">Import a Chess.com Game</h3>
            <p className="card-text">Paste a game link such as https://www.chess.com/game/live/143645010490.</p>
            <form onSubmit={handleImport} className="row g-2">
              <div className="col-md-9">
                <input
                  type="url"
                  className="form-control"
                  placeholder="https://www.chess.com/game/live/123456789"
                  value={importUrl}
                  onChange={(event) => setImportUrl(event.target.value)}
                  disabled={importing}
                  required
                />
              </div>
              <div className="col-md-3 d-grid">
                <button type="submit" className="btn btn-success" disabled={importing}>
                  {importing ? 'Importing…' : 'Import Game'}
                </button>
              </div>
            </form>
            {importStatus && <div className="mt-2">{importStatus}</div>}
          </div>
        </div>
      </div>

      <div className="col-12">
        <h2>Recent Games</h2>
        {games.length > 0 ? (
          <div className="row">
            {games.map((game) => (
              <div key={game.id} className="col-md-4 mb-3">
                <Link href={`/game/${game.id}`} className="text-decoration-none">
                  <div className="card game-card h-100">
                    <div className="card-body">
                      <h5 className="card-title">{game.title}</h5>
                      <p className="card-text">
                        {game.user_color === 'w' ? (
                          <span><strong>{user?.username} (White)</strong> vs <strong>{game.opponent_name || 'Anonymous'}</strong></span>
                        ) : (
                          <span><strong>{game.opponent_name || 'Anonymous'}</strong> vs <strong>{user?.username} (Black)</strong></span>
                        )}
                      </p>
                      <div className="d-flex justify-content-between align-items-center">
                        <small className="text-muted">
                          {new Date(game.created_at).toLocaleDateString()}
                        </small>
                        <span
                          className={`badge bg-${
                            game.status === 'completed' ? 'success' : 'primary'
                          }`}
                        >
                          {game.status}
                        </span>
                      </div>
                      {game.result !== '*' && (
                        <small className="text-muted">Result: {game.result}</small>
                      )}
                    </div>
                  </div>
                </Link>
              </div>
            ))}
          </div>
        ) : (
          <div className="alert alert-info">
            <h4>No games yet!</h4>
            <p>Get started by creating a sample game to see Chessaroo in action.</p>
            <button onClick={createSampleGame} className="btn btn-primary">
              Create Sample Game
            </button>
          </div>
        )}
      </div>

    </div>
  );
}
