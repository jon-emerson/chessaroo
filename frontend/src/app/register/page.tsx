'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '../../contexts/AuthContext';

export default function RegisterPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { register } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (username.length < 3) {
      setError('Username must be at least 3 characters long');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }

    setIsLoading(true);

    try {
      await register(email, password, username);
      router.push('/');
    } catch (err: any) {
      setError(err.message || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mx-auto grid max-w-3xl gap-10">
      <div className="surface-card space-y-8">
        <div className="space-y-3 text-center">
          <span className="pill-muted mx-auto">Join the lab</span>
          <h2 className="text-3xl font-semibold text-white">Create your BlunderLab account</h2>
          <p className="text-sm text-slate-400">
            BlunderLab turns every loss into a lesson. Create a free account to fingerprint your tactical
            habits and build the study playlists that fix them.
          </p>
        </div>

        {error && (
          <div className="rounded-2xl border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="grid gap-6 md:grid-cols-2">
          <div className="space-y-2">
            <label htmlFor="username" className="field-label">
              Username
            </label>
            <input
              type="text"
              className="input-field"
              id="username"
              name="username"
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={isLoading}
              minLength={3}
              maxLength={50}
              inputMode="text"
              autoCapitalize="none"
              spellCheck={false}
              pattern="^[^@\s]+$"
              title="Username cannot contain spaces or @"
              placeholder="queencrusher"
            />
            <p className="form-hint">Other players will see this handle on your shared reports.</p>
          </div>

          <div className="space-y-2">
            <label htmlFor="email" className="field-label">
              Email address
            </label>
            <input
              type="email"
              className="input-field"
              id="email"
              name="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={isLoading}
              placeholder="you@example.com"
            />
            <p className="form-hint">We keep it private—purely for sign-in and account recovery.</p>
          </div>

          <div className="space-y-2">
            <label htmlFor="password" className="field-label">
              Password
            </label>
            <input
              type="password"
              className="input-field"
              id="password"
              name="password"
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={isLoading}
              minLength={6}
              placeholder="Create a secure passphrase"
            />
            <p className="form-hint">Minimum 6 characters. Longer phrases beat single words.</p>
          </div>

          <div className="space-y-2">
            <label htmlFor="confirmPassword" className="field-label">
              Confirm password
            </label>
            <input
              type="password"
              className="input-field"
              id="confirmPassword"
              name="confirmPassword"
              autoComplete="new-password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              disabled={isLoading}
              placeholder="Repeat your password"
            />
          </div>

          <div className="md:col-span-2">
            <button type="submit" className="btn-primary w-full" disabled={isLoading}>
              {isLoading ? 'Creating account…' : 'Create account'}
            </button>
          </div>
        </form>

        <div className="rounded-2xl border border-slate-800/70 bg-slate-900/60 px-4 py-3 text-sm text-slate-300">
          <strong className="text-slate-100">Heads up:</strong> Your username is public. Your email stays private.
        </div>

        <div className="text-center text-sm text-slate-400">
          Already have an account?{' '}
          <Link href="/login" className="text-cyan-300 hover:text-cyan-200">
            Log in instead
          </Link>
        </div>
      </div>
    </div>
  );
}
