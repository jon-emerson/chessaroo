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

export default function AdminPage() {
  const [password, setPassword] = useState('');
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkSession = async () => {
      try {
        const data = await apiCall('/api/admin/users');
        setUsers(data.users || []);
        setIsAuthenticated(true);
      } catch (err) {
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
      await apiCall('/api/admin/login', {
        method: 'POST',
        body: JSON.stringify({ password }),
      });
      const data = await apiCall('/api/admin/users');
      setUsers(data.users || []);
      setIsAuthenticated(true);
      setPassword('');
    } catch (err: any) {
      setError(err?.message || 'Failed to authenticate');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleLogout = async () => {
    try {
      await apiCall('/api/admin/logout', { method: 'POST' });
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
    } catch (e) {
      return value;
    }
  };

  if (isLoading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '60vh' }}>
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-2">Checking admin session...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card">
            <div className="card-body">
              <h3 className="card-title mb-3">Admin</h3>
              <form onSubmit={handleLogin}>
                <div className="mb-3">
                  <input
                    id="admin-password"
                    type="password"
                    className="form-control"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="Password"
                    disabled={isSubmitting}
                  />
                </div>
                {error && <div className="alert alert-danger">{error}</div>}
                <button type="submit" className="btn btn-dark w-100" disabled={isSubmitting}>
                  {isSubmitting ? 'Authenticating...' : 'Login'}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header d-flex justify-content-between align-items-center">
        <h3 className="card-title mb-0">Users</h3>
        <button className="btn btn-outline-secondary btn-sm" onClick={handleLogout}>
          Logout
        </button>
      </div>
      <div className="card-body">
        {users.length === 0 ? (
          <div className="alert alert-info mb-0">No users found in the database.</div>
        ) : (
          <div className="table-responsive">
            <table className="table table-striped table-hover align-middle">
              <thead className="table-dark">
                <tr>
                  <th scope="col">User ID</th>
                  <th scope="col">Username</th>
                  <th scope="col">Email</th>
                  <th scope="col">Created</th>
                  <th scope="col">Last Updated</th>
                  <th scope="col">Last Login</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.user_id}>
                    <td><code>{user.user_id}</code></td>
                    <td>{user.username}</td>
                    <td>{user.email}</td>
                    <td>{formatDate(user.created_at)}</td>
                    <td>{formatDate(user.updated_at)}</td>
                    <td>{formatDate(user.last_login)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
