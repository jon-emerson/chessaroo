'use client';

import Link from 'next/link';
import { useAuth } from '../contexts/AuthContext';

export default function Navigation() {
  const { user, isAuthenticated } = useAuth();

  return (
    <header className="sticky top-0 z-40 border-b border-slate-800/70 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-4 sm:px-8 lg:px-10">
        <Link
          href="/"
          className="group inline-flex items-center gap-3 text-lg font-semibold tracking-tight text-white"
        >
          <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400/80 via-sky-500/80 to-purple-500/80 text-2xl text-slate-950 shadow-glow transition group-hover:scale-105">
            <span className="-mt-0.5 scale-125 text-4xl leading-none">♞</span>
          </span>
          <div className="flex flex-col">
            <span className="text-sm uppercase tracking-[0.3em] text-slate-400">BlunderLab</span>
            <span className="text-base font-semibold text-white">
              Chess Intelligence for Relentless Improvers
            </span>
          </div>
        </Link>

        <nav className="flex items-center gap-4 text-sm font-medium text-slate-300">
          <Link
            href="/"
            className="rounded-full px-3 py-1.5 transition hover:bg-slate-900/70 hover:text-white"
          >
            Overview
          </Link>
          {isAuthenticated ? (
            <>
              <Link
                href="/home"
                className="rounded-full px-3 py-1.5 transition hover:bg-slate-900/70 hover:text-white"
              >
                Dashboard
              </Link>
              <Link
                href="/settings"
                className="rounded-full px-3 py-1.5 transition hover:bg-slate-900/70 hover:text-white"
              >
                {user?.username}
              </Link>
              <Link href="/home" className="btn-primary hidden sm:inline-flex">
                Analyze a game
              </Link>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="rounded-full px-3 py-1.5 transition hover:bg-slate-900/70 hover:text-white"
              >
                Log in
              </Link>
              <Link href="/register" className="btn-primary">
                Create account
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
