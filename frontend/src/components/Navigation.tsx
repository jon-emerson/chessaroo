'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { apiCall } from '../lib/api';

export default function Navigation() {
  const router = useRouter();

  const handleCreateSample = async (e: React.MouseEvent) => {
    e.preventDefault();
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

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
      <div className="container">
        <Link className="navbar-brand" href="/">
          ♕ Chessaroo
        </Link>
        <div className="navbar-nav ms-auto">
          <Link className="nav-link" href="/">
            Games
          </Link>
          <button
            className="nav-link btn btn-link text-decoration-none"
            onClick={handleCreateSample}
            style={{ border: 'none', background: 'none', color: 'rgba(255,255,255,.55)' }}
          >
            Create Sample
          </button>
        </div>
      </div>
    </nav>
  );
}