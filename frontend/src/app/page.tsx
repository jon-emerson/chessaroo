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
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="flex flex-col items-center gap-4 text-center">
          <span className="h-12 w-12 animate-spin rounded-full border-2 border-slate-700/80 border-t-cyan-400" />
          <p className="text-sm text-slate-400">Loading your opening book…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-16">
      <section className="relative overflow-hidden rounded-3xl border border-slate-800/80 bg-hero-gradient px-6 py-16 sm:px-10">
        <div className="absolute inset-y-0 right-0 hidden w-1/2 max-w-md translate-x-1/4 grid-highlight opacity-40 lg:block" />
        <div className="relative z-10 grid gap-12 lg:grid-cols-2 lg:items-center">
          <div className="flex flex-col gap-6">
            <span className="pill-muted w-max">Chess strength is a choice</span>
            <h1 className="leading-tight text-white">
              Diagnose the patterns behind your losses. Train like the players who beat you.
            </h1>
            <p className="max-w-xl text-lg text-slate-300">
              BlunderLab ingests your Chess.com games, fingerprints the tactical traps you fall for, and
              hands you a focused training plan before your next match. No more vague advice—just data,
              discipline, and deliberate practice.
            </p>
            <div className="flex flex-wrap items-center gap-3">
              <Link href="/register" className="btn-primary">
                Start analyzing my games
              </Link>
              <Link href="/login" className="btn-secondary">
                I already have an account
              </Link>
            </div>
            <dl className="mt-8 grid grid-cols-1 gap-5 text-sm text-slate-300 sm:grid-cols-3">
              <div className="surface-card bg-slate-900/75 p-4">
                <dt className="text-xs uppercase tracking-wide text-slate-500">Blunders Tagged</dt>
                <dd className="mt-2 text-2xl font-semibold text-white">42,917+</dd>
              </div>
              <div className="surface-card bg-slate-900/75 p-4">
                <dt className="text-xs uppercase tracking-wide text-slate-500">Tactical Themes</dt>
                <dd className="mt-2 text-2xl font-semibold text-white">31 patterns</dd>
              </div>
              <div className="surface-card bg-slate-900/75 p-4">
                <dt className="text-xs uppercase tracking-wide text-slate-500">Average Rating Lift</dt>
                <dd className="mt-2 text-2xl font-semibold text-white">+86 Elo</dd>
              </div>
            </dl>
          </div>

          <div className="relative flex justify-center lg:justify-end">
            <div className="surface-card-xl relative max-w-md space-y-6">
              <div className="pill-muted">Live demo</div>
              <p className="text-base text-slate-300">
                "BlunderLab caught that I lose focus in opposite-colored bishop endgames. The drills
                turned my endgame results upside down." —<span className="text-cyan-300"> Alex, 1820 rapid</span>
              </p>
              <div className="grid gap-3 text-sm text-slate-300">
                <div className="rounded-2xl border border-slate-800/70 bg-slate-900/70 px-4 py-3">
                  <p className="text-xs uppercase tracking-wide text-slate-500">Recurring trap</p>
                  <p className="mt-1 font-medium text-white">Pinned knight sacs after g-file pawn storms</p>
                </div>
                <div className="rounded-2xl border border-slate-800/70 bg-slate-900/70 px-4 py-3">
                  <p className="text-xs uppercase tracking-wide text-slate-500">Repair this opening</p>
                  <p className="mt-1 font-medium text-white">Bishop's Opening → Vienna Gambit sideline</p>
                </div>
                <div className="rounded-2xl border border-slate-800/70 bg-slate-900/70 px-4 py-3">
                  <p className="text-xs uppercase tracking-wide text-slate-500">Drill pack</p>
                  <p className="mt-1 font-medium text-white">12 exercises • 9 minutes/day • 5 day sprint</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 md:grid-cols-3">
        {[
          {
            title: 'Pattern fingerprinting',
            description:
              'Cluster every blunder by tactical theme so you can attack the exact calculation habits that leak rating points.',
          },
          {
            title: 'Opening repair briefs',
            description:
              'Compare your score to master databases and get focused repair lines for the move-number where games go sideways.',
          },
          {
            title: 'Study-ready exports',
            description:
              'Push curated positions directly into your spaced-repetition system or share a PDF with your coach in one click.',
          },
        ].map((feature) => (
          <div key={feature.title} className="surface-card h-full">
            <h3 className="text-lg font-semibold text-white">{feature.title}</h3>
            <p className="mt-3 text-sm leading-6 text-slate-300">{feature.description}</p>
          </div>
        ))}
      </section>

      <section className="surface-card-xl grid gap-10 lg:grid-cols-2">
        <div className="space-y-6">
          <span className="pill-muted">How it works</span>
          <h2 className="text-3xl font-semibold text-white">Three steps to blunder-proofing your repertoire</h2>
          <p className="text-base text-slate-300">
            Upload a game, let BlunderLab auto-tag every mistake, and focus on the moves that matter. No
            spammy puzzles. No guesswork. Just the habits that decide your next time-pressure scramble.
          </p>
        </div>
        <ol className="space-y-4 text-sm text-slate-300">
          <li className="surface-card bg-slate-900/80 p-5">
            <p className="text-xs uppercase tracking-wide text-slate-500">Step 1</p>
            <p className="mt-2 font-semibold text-white">Import a Chess.com or Lichess slug</p>
            <p className="mt-1 text-sm text-slate-300">
              We pull the raw PGN, evaluate with our motif engine, and cross-reference past games to spot
              recurring situations.
            </p>
          </li>
          <li className="surface-card bg-slate-900/80 p-5">
            <p className="text-xs uppercase tracking-wide text-slate-500">Step 2</p>
            <p className="mt-2 font-semibold text-white">Diagnose your tactical fingerprint</p>
            <p className="mt-1 text-sm text-slate-300">
              Heatmaps show where you overpress, miss quiet resources, or forget endgame fundamentals.
            </p>
          </li>
          <li className="surface-card bg-slate-900/80 p-5">
            <p className="text-xs uppercase tracking-wide text-slate-500">Step 3</p>
            <p className="mt-2 font-semibold text-white">Run the targeted training sprint</p>
            <p className="mt-1 text-sm text-slate-300">
              Export targeted drills to your trainer of choice and log the score lift after every analysis
              cycle.
            </p>
          </li>
        </ol>
      </section>
    </div>
  );
}
