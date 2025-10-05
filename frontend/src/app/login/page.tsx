'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '../../contexts/AuthContext';

export default function LoginPage() {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login(identifier, password);
      router.push('/home');
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mx-auto grid max-w-lg gap-8">
      <div className="surface-card space-y-6">
        <div className="space-y-2 text-center">
          <span className="pill-muted mx-auto">Welcome back</span>
          <h2 className="text-2xl font-semibold text-white">Log in to BlunderLab</h2>
          <p className="text-sm text-slate-400">
            Drop straight into your dashboard, surface the blunders you made last night, and queue the next
            study sprint.
          </p>
        </div>

        {error && (
          <div className="rounded-2xl border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-2">
            <label htmlFor="identifier" className="field-label">
              Username or Email
            </label>
            <input
              type="text"
              className="input-field"
              id="identifier"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              required
              disabled={isLoading}
              autoComplete="username"
              inputMode="text"
              autoCapitalize="none"
              spellCheck={false}
              placeholder="alex@blunderlab.com"
            />
            <p className="form-hint">Use either your BlunderLab handle or the email tied to your account.</p>
          </div>

          <div className="space-y-2">
            <label htmlFor="password" className="field-label">
              Password
            </label>
            <input
              type="password"
              className="input-field"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={isLoading}
              placeholder="••••••••"
            />
          </div>

          <button type="submit" className="btn-primary w-full" disabled={isLoading}>
            {isLoading ? 'Logging in…' : 'Log in'}
          </button>
        </form>

        <div className="text-center text-sm text-slate-400">
          Don&apos;t have an account?{' '}
          <Link href="/register" className="text-cyan-300 hover:text-cyan-200">
            Create one for free
          </Link>
        </div>
      </div>
    </div>
  );
}
