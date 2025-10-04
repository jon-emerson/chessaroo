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
      <div className="loading-spinner">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (error || !details) {
    return (
      <div className="alert alert-danger">
        <h4>Import Not Found</h4>
        <p>{error || 'We could not find that imported game.'}</p>
        <button onClick={() => router.push('/')} className="btn btn-primary">
          ← Back to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="row">
      <div className="col-12 mb-3">
        <button onClick={() => router.push('/')} className="btn btn-outline-secondary btn-sm">
          ← Back to Dashboard
        </button>
      </div>

      <div className="col-12">
        <h1>Imported Chess.com Game</h1>
        <p className="text-muted">Chess.com Game ID: {details.chessComGameId}</p>
      </div>

      <div className="col-lg-6">
        <div className="card mb-3">
          <div className="card-body">
            <h4 className="card-title">Players</h4>
            <p><strong>White:</strong> {details.whiteUsername || 'Unknown'}</p>
            <p><strong>Black:</strong> {details.blackUsername || 'Unknown'}</p>
            <p><strong>Result:</strong> {details.resultMessage || 'Pending'}</p>
            <p><strong>Status:</strong> {details.isFinished ? 'Finished' : 'In Progress'}</p>
            {details.gameEndReason && (
              <p><strong>Game End Reason:</strong> {details.gameEndReason}</p>
            )}
          </div>
        </div>
      </div>

      <div className="col-lg-6">
        <div className="card mb-3">
          <div className="card-body">
            <h4 className="card-title">Metadata</h4>
            <p><strong>Imported At:</strong> {details.importedAt ? new Date(details.importedAt).toLocaleString() : '—'}</p>
            <p><strong>End Time:</strong> {details.endTime ? new Date(details.endTime).toLocaleString() : '—'}</p>
            <p><strong>Time Control:</strong> {details.timeControl || '—'}</p>
            <p><strong>Chess.com UUID:</strong> {details.uuid || '—'}</p>
            <p>
              <strong>Source URL:</strong>{' '}
              <a href={details.sourceUrl} target="_blank" rel="noopener noreferrer">
                View on Chess.com
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
