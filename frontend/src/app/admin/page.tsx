'use client';

import { useEffect, useState } from 'react';
import { apiCall } from '../../lib/api';

interface AdminUser {
  user_id: string;
  username: string;
  email: string;
  created_at: string | null;
  updated_at: string | null;
  last_login: string | null;
}

interface AdminStatus {
  configured: boolean;
  authenticated: boolean;
}

export default function AdminPage() {
  const [password, setPassword] = useState('');
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isConfigured, setIsConfigured] = useState<boolean | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusError, setStatusError] = useState<string | null>(null);

  useEffect(() => {
    const checkSession = async () => {
      try {
        const status = (await apiCall('/admin/status')) as AdminStatus;
        setIsConfigured(Boolean(status.configured));

        if (status.configured && status.authenticated) {
          const data = await apiCall('/admin/users');
          setUsers(data.users || []);
          setIsAuthenticated(true);
        } else {
          setIsAuthenticated(false);
        }
      } catch (err: any) {
        const message = err?.message || 'Unable to load admin status';
        setStatusError(message);
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkSession();
  }, []);

  const handleLogin = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);

    if (!password) {
      setError('Please enter the admin master password.');
      return;
    }

    setIsSubmitting(true);
    try {
      await apiCall('/admin/login', {
        method: 'POST',
        body: JSON.stringify({ password }),
      });
      const data = await apiCall('/admin/users');
      setUsers(data.users || []);
      setIsAuthenticated(true);
      setIsConfigured(true);
      setPassword('');
    } catch (err: any) {
      setError(err?.message || 'Failed to authenticate');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleLogout = async () => {
    try {
      await apiCall('/admin/logout', { method: 'POST' });
    } catch (err) {
      // Ignore errors on logout
    } finally {
      setIsAuthenticated(false);
      setUsers([]);
    }
  };

  const formatDate = (value: string | null) => {
    if (!value) return '—';
    try {
      return new Date(value).toLocaleString();
    } catch {
      return value;
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="flex flex-col items-center gap-4 text-center">
          <span className="h-12 w-12 animate-spin rounded-full border-2 border-slate-700/80 border-t-cyan-400" />
          <p className="text-sm text-slate-400">Checking admin session…</p>
        </div>
      </div>
    );
  }

  if (isConfigured === false) {
    return (
      <div className="surface-card space-y-4 text-sm text-slate-300">
        <h3 className="text-xl font-semibold text-white">Admin disabled</h3>
        <p>
          The admin master password is not configured. Set the <code className="rounded bg-slate-900/70 px-1.5 py-0.5">ADMIN_MASTER_PASSWORD</code>
          environment variable (or <code className="rounded bg-slate-900/70 px-1.5 py-0.5">ADMIN_MASTER_PASSWORD_DEV</code> for development) and redeploy to enable this
          page.
        </p>
        <p className="text-slate-400">
          This safeguard prevents exposing admin endpoints without authentication. Update your deployment secrets and reload once configured.
        </p>
      </div>
    );
  }

  if (statusError) {
    return (
      <div className="surface-card border border-rose-500/40 bg-rose-500/10 px-4 py-4 text-sm text-rose-200">
        {statusError}
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="mx-auto max-w-md">
        <div className="surface-card space-y-6">
          <div className="text-center">
            <h3 className="text-xl font-semibold text-white">Admin login</h3>
            <p className="mt-2 text-sm text-slate-400">
              Enter the master password to view account insights. This password is never shared with regular users.
            </p>
          </div>
          <form onSubmit={handleLogin} className="space-y-4">
            <input
              id="admin-password"
              type="password"
              className="input-field"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Master password"
              disabled={isSubmitting}
            />
            {error && (
              <div className="rounded-2xl border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
                {error}
              </div>
            )}
            <button type="submit" className="btn-primary w-full" disabled={isSubmitting}>
              {isSubmitting ? 'Authenticating…' : 'Login'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <section className="surface-card space-y-6">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-2xl font-semibold text-white">Users</h3>
          <p className="text-sm text-slate-400">This view is only available to administrators with the master password.</p>
        </div>
        <button className="btn-secondary" onClick={handleLogout}>
          Logout
        </button>
      </header>

      {users.length === 0 ? (
        <div className="rounded-2xl border border-slate-800/70 bg-slate-900/60 px-4 py-3 text-sm text-slate-300">
          No users found in the database.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-2xl border border-slate-800/70">
          <table className="min-w-full divide-y divide-slate-800/70 text-left text-sm text-slate-300">
            <thead className="bg-slate-900/80 text-xs uppercase tracking-wide text-slate-400">
              <tr>
                <th className="px-4 py-3">User ID</th>
                <th className="px-4 py-3">Username</th>
                <th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Created</th>
                <th className="px-4 py-3">Last Updated</th>
                <th className="px-4 py-3">Last Login</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {users.map((user) => (
                <tr key={user.user_id} className="hover:bg-slate-900/70">
                  <td className="px-4 py-3 font-mono text-xs text-slate-400">{user.user_id}</td>
                  <td className="px-4 py-3 text-white">{user.username}</td>
                  <td className="px-4 py-3 text-slate-300">{user.email}</td>
                  <td className="px-4 py-3">{formatDate(user.created_at)}</td>
                  <td className="px-4 py-3">{formatDate(user.updated_at)}</td>
                  <td className="px-4 py-3">{formatDate(user.last_login)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
