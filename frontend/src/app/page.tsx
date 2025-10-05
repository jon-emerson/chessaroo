'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '../contexts/AuthContext';

export default function LandingPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.replace('/home');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
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
      <div className="col-12 text-center">
        <h1>♕ Welcome to Chessaroo</h1>
        <p className="lead">
          Import your Chess.com games, surface the patterns behind your losses, and get actionable study
          prompts for the tactics that repeatedly catch you off guard.
        </p>
        <div className="d-flex justify-content-center gap-2 mb-4">
          <Link href="/login" className="btn btn-primary">
            Log In
          </Link>
          <Link href="/register" className="btn btn-outline-primary">
            Create an Account
          </Link>
        </div>
      </div>

      <div className="col-12">
        <div className="row g-3">
          <div className="col-md-4">
            <div className="card h-100 shadow-sm">
              <div className="card-body">
                <h4 className="card-title">Recurring Tactical Mistakes</h4>
                <p className="card-text">
                  Chessaroo scans your imported games for repeat offenders—pins, skewers, forks, and
                  opposition blunders—so you can drill the exact pattern that keeps costing rating points.
                </p>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card h-100 shadow-sm">
              <div className="card-body">
                <h4 className="card-title">Opening Repair Suggestions</h4>
                <p className="card-text">
                  We highlight openings you navigate poorly and recommend concrete alternative moves drawn
                  from stronger lines you already encounter.
                </p>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card h-100 shadow-sm">
              <div className="card-body">
                <h4 className="card-title">Study-Ready Exports</h4>
                <p className="card-text">
                  Export curated lists of problem spots for spaced repetition tools or share insight
                  snapshots with coaches and training partners.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
