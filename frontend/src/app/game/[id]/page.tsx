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
  const [currentMoveIndex, setCurrentMoveIndex] = useState(-1);
  const [boardPosition, setBoardPosition] = useState<string>('');
  const [chess] = useState(new Chess());
  const [boardWidth, setBoardWidth] = useState(600);

  useEffect(() => {
    if (gameId) {
      fetchGameData();
    }
  }, [gameId]);

  useEffect(() => {
    const updateBoardWidth = () => {
      setBoardWidth(Math.min(600, window.innerWidth - 48));
    };

    updateBoardWidth();
    window.addEventListener('resize', updateBoardWidth);
    return () => window.removeEventListener('resize', updateBoardWidth);
  }, []);

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
        default:
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentMoveIndex, gameData]);

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
    if (moveIndex < -1 || moveIndex >= gameData.moves.length) return;

    setCurrentMoveIndex(moveIndex);
    const targetFen = moveIndex === -1 ? gameData.startingFen : gameData.moves[moveIndex].fen;
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

  const goToStart = () => goToMove(-1);

  const goToEnd = () => {
    if (gameData) {
      goToMove(gameData.moves.length - 1);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="flex flex-col items-center gap-4 text-center">
          <span className="h-12 w-12 animate-spin rounded-full border-2 border-slate-700/80 border-t-cyan-400" />
          <p className="text-sm text-slate-400">Loading game state…</p>
        </div>
      </div>
    );
  }

  if (error || !gameData) {
    return (
      <div className="surface-card space-y-4 text-sm text-slate-300">
        <h2 className="text-xl font-semibold text-white">Could not load this game</h2>
        <p>{error || 'Game not found'}</p>
        <button onClick={() => router.push('/')} className="btn-secondary w-max">
          ← Back to games
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <button onClick={() => router.push('/')} className="btn-secondary">
        ← Back to games
      </button>

      <section className="surface-card space-y-6">
        <div className="grid gap-6 md:grid-cols-2">
          <div>
            <h2 className="text-2xl font-semibold text-white">{gameData.title}</h2>
            <p className="mt-2 text-sm text-slate-300">
              <span className="text-slate-400">Opponent:</span> {gameData.opponentName || 'Anonymous'}
            </p>
            <p className="text-sm text-slate-300">
              <span className="text-slate-400">Playing as:</span> {gameData.userColor === 'w' ? 'White' : 'Black'}
            </p>
          </div>
          <div className="grid gap-3 text-sm text-slate-300 sm:grid-cols-2">
            <div className="rounded-2xl border border-slate-800/60 bg-slate-900/60 px-4 py-3">
              <p className="text-xs uppercase tracking-wide text-slate-500">Game ID</p>
              <p className="mt-1 font-semibold text-white">{gameData.gameId}</p>
            </div>
            <div className="rounded-2xl border border-slate-800/60 bg-slate-900/60 px-4 py-3">
              <p className="text-xs uppercase tracking-wide text-slate-500">Moves</p>
              <p className="mt-1 font-semibold text-white">{gameData.moves.length}</p>
            </div>
          </div>
        </div>

        <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_320px]">
          <div className="space-y-6">
            <div className="rounded-3xl border border-slate-800/70 bg-slate-900/70 p-4 shadow-lg">
              <Chessboard
                position={boardPosition}
                boardOrientation={gameData.userColor === 'w' ? 'white' : 'black'}
                arePiecesDraggable={false}
                customDarkSquareStyle={{ backgroundColor: '#0f172a' }}
                customLightSquareStyle={{ backgroundColor: '#1e293b' }}
                animationDuration={150}
                boardWidth={boardWidth}
                customBoardStyle={{ borderRadius: '1.5rem', boxShadow: '0 30px 80px -40px rgba(15,23,42,0.9)' }}
              />
            </div>

            <div className="flex flex-wrap gap-3">
              <button onClick={goToStart} className="btn-secondary text-xs uppercase tracking-wide">
                ⏮ Start
              </button>
              <button onClick={goToPreviousMove} className="btn-secondary text-xs uppercase tracking-wide">
                ◀ Prev
              </button>
              <button onClick={goToNextMove} className="btn-secondary text-xs uppercase tracking-wide">
                Next ▶
              </button>
              <button onClick={goToEnd} className="btn-secondary text-xs uppercase tracking-wide">
                End ⏭
              </button>
            </div>
          </div>

          <aside className="flex flex-col gap-4">
            <div className="rounded-2xl border border-slate-800/70 bg-slate-900/60 px-5 py-4">
              <h3 className="text-lg font-semibold text-white">Move list</h3>
              <p className="mt-1 text-xs text-slate-400">
                Tip: Use ← and → to navigate. Home jumps to the start; End jumps to the final position.
              </p>
            </div>
            <div className="flex-1 space-y-2 overflow-y-auto rounded-2xl border border-slate-800/70 bg-slate-900/60 p-4">
              {gameData.moves.map((move, index) => {
                const isActive = index === currentMoveIndex;
                return (
                  <button
                    key={`${move.moveNumber}-${move.color}`}
                    onClick={() => goToMove(index)}
                    className={`flex w-full items-center justify-between rounded-xl px-4 py-2 text-sm transition ${
                      isActive
                        ? 'bg-cyan-500/15 text-cyan-200 shadow-glow'
                        : 'bg-slate-900/80 text-slate-300 hover:bg-slate-800/80'
                    }`}
                  >
                    <span className="font-medium text-white">
                      {move.moveNumber}
                      {move.color === 'w' ? '.' : '...'}
                    </span>
                    <span>{move.algebraic}</span>
                  </button>
                );
              })}
            </div>
          </aside>
        </div>
      </section>
    </div>
  );
}
