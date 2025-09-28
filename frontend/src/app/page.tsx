'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
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
  const { user } = useAuth();
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

  const createSampleGame = async () => {
    try {
      const response = await apiCall('/api/create-sample-game');
      if (response.gameId) {
        // Refresh the page to show the new game
        window.location.reload();
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

      <div className="col-md-8">
        <h2>Recent Games</h2>
        {games.length > 0 ? (
          <div className="row">
            {games.map((game) => (
              <div key={game.id} className="col-md-6 mb-3">
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

      <div className="col-md-4">
        <div className="card">
          <div className="card-header">
            <h5>About Chessaroo</h5>
          </div>
          <div className="card-body">
            <p>Chessaroo is a multiplayer chess application built with:</p>
            <ul>
              <li>Next.js + React frontend</li>
              <li>Flask API backend</li>
              <li>PostgreSQL database</li>
              <li>Chess.js for game logic</li>
              <li>React Chessboard for visualization</li>
              <li>AWS cloud infrastructure</li>
            </ul>
            <p>
              Each game stores moves in standard algebraic notation with full board state
              (FEN) for perfect game reconstruction.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}