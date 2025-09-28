'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Chess } from 'chess.js';
import { Chessboard } from 'react-chessboard';
import { apiCall } from '../../../lib/api';

interface Move {
  moveNumber: number;
  color: 'w' | 'b';
  algebraic: string;
  fen: string;
}

interface GameData {
  gameId: number;
  title: string;
  userColor: string;
  opponentName: string;
  startingFen: string;
  currentFen: string;
  moves: Move[];
}

export default function GamePage() {
  const params = useParams();
  const router = useRouter();
  const gameId = params.id as string;

  const [gameData, setGameData] = useState<GameData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentMoveIndex, setCurrentMoveIndex] = useState(-1); // -1 = starting position
  const [boardPosition, setBoardPosition] = useState<string>('');
  const [chess] = useState(new Chess());
  const [boardWidth, setBoardWidth] = useState(600);

  useEffect(() => {
    if (gameId) {
      fetchGameData();
    }
  }, [gameId]);

  useEffect(() => {
    // Set board width based on screen size
    const updateBoardWidth = () => {
      setBoardWidth(Math.min(600, window.innerWidth - 50));
    };

    updateBoardWidth();
    window.addEventListener('resize', updateBoardWidth);

    return () => window.removeEventListener('resize', updateBoardWidth);
  }, []);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      switch (event.key) {
        case 'ArrowLeft':
          event.preventDefault();
          goToPreviousMove();
          break;
        case 'ArrowRight':
          event.preventDefault();
          goToNextMove();
          break;
        case 'Home':
          event.preventDefault();
          goToStart();
          break;
        case 'End':
          event.preventDefault();
          goToEnd();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentMoveIndex, gameData]); // Dependencies to ensure functions have latest state

  const fetchGameData = async () => {
    try {
      const data: GameData = await apiCall(`/api/game/${gameId}/moves`);
      setGameData(data);
      setBoardPosition(data.startingFen);
      chess.load(data.startingFen);
      setLoading(false);
    } catch (err) {
      console.error('Error loading game data:', err);
      setError(`Failed to load game data: ${err instanceof Error ? err.message : 'Unknown error'}`);
      setLoading(false);
    }
  };

  const goToMove = (moveIndex: number) => {
    if (!gameData) return;

    // Validate move index
    if (moveIndex < -1 || moveIndex >= gameData.moves.length) {
      return;
    }

    setCurrentMoveIndex(moveIndex);

    let targetFen: string;
    if (moveIndex === -1) {
      // Starting position
      targetFen = gameData.startingFen;
    } else {
      // Specific move
      targetFen = gameData.moves[moveIndex].fen;
    }

    setBoardPosition(targetFen);
    chess.load(targetFen);
  };

  const goToPreviousMove = () => {
    if (currentMoveIndex > -1) {
      goToMove(currentMoveIndex - 1);
    }
  };

  const goToNextMove = () => {
    if (gameData && currentMoveIndex < gameData.moves.length - 1) {
      goToMove(currentMoveIndex + 1);
    }
  };

  const goToStart = () => {
    goToMove(-1);
  };

  const goToEnd = () => {
    if (gameData) {
      goToMove(gameData.moves.length - 1);
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

  if (error || !gameData) {
    return (
      <div className="alert alert-danger">
        <h4>Error</h4>
        <p>{error || 'Game not found'}</p>
        <button onClick={() => router.push('/')} className="btn btn-primary">
          ← Back to Games
        </button>
      </div>
    );
  }

  return (
    <div>
      <div className="row mb-3">
        <div className="col-12">
          <button onClick={() => router.push('/')} className="btn btn-outline-secondary btn-sm">
            ← Back to Games
          </button>
        </div>
      </div>

      <div className="game-info">
        <div className="row">
          <div className="col-md-6">
            <h2>{gameData.title}</h2>
            <p>
              <strong>Opponent:</strong> {gameData.opponentName || 'Anonymous'}
            </p>
            <p>
              <strong>Playing as:</strong> {gameData.userColor === 'w' ? 'White' : 'Black'}
            </p>
          </div>
          <div className="col-md-6 text-end">
            <p>
              <strong>Game ID:</strong> {gameData.gameId}
            </p>
            <p>
              <strong>Moves:</strong> {gameData.moves.length}
            </p>
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-lg-8">
          <div className="chess-board-container">
            <Chessboard
              position={boardPosition}
              arePiecesDraggable={false}
              boardWidth={boardWidth}
            />
          </div>

          <div className="mt-3 text-center">
            <button
              onClick={goToPreviousMove}
              className="btn btn-outline-primary btn-sm me-2"
              disabled={currentMoveIndex <= -1}
            >
              ← Previous
            </button>
            <button onClick={goToStart} className="btn btn-outline-secondary btn-sm me-2">
              Start
            </button>
            <button onClick={goToEnd} className="btn btn-outline-secondary btn-sm me-2">
              End
            </button>
            <button
              onClick={goToNextMove}
              className="btn btn-outline-primary btn-sm"
              disabled={currentMoveIndex >= gameData.moves.length - 1}
            >
              Next →
            </button>
          </div>
        </div>

        <div className="col-lg-4">
          <h4>Moves</h4>
          <div className="move-list">
            <div
              className={`move-item ${currentMoveIndex === -1 ? 'active' : ''}`}
              onClick={() => goToMove(-1)}
            >
              <strong>Starting position</strong>
            </div>
            {gameData.moves.map((move, index) => (
              <div
                key={index}
                className={`move-item ${currentMoveIndex === index ? 'active' : ''}`}
                onClick={() => goToMove(index)}
              >
                <strong>
                  {move.moveNumber}
                  {move.color === 'w' ? '.' : '...'}
                </strong>{' '}
                {move.algebraic}
              </div>
            ))}
          </div>

          <div className="mt-3">
            <h5>Current Position</h5>
            <div className="card">
              <div className="card-body">
                <small className="font-monospace text-muted">{boardPosition}</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}