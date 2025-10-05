'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../contexts/AuthContext';

export default function SettingsPage() {
  const { user, logout, updateProfile, changePassword } = useAuth();
  const router = useRouter();

  // Profile form state
  const [username, setUsername] = useState(user?.username || '');
  const [email, setEmail] = useState(user?.email || '');
  const [profileError, setProfileError] = useState('');
  const [profileSuccess, setProfileSuccess] = useState('');
  const [profileLoading, setProfileLoading] = useState(false);

  // Password form state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState('');
  const [passwordLoading, setPasswordLoading] = useState(false);

  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileError('');
    setProfileSuccess('');
    setProfileLoading(true);

    try {
      await updateProfile(username, email);
      setProfileSuccess('Profile updated successfully!');
    } catch (err: any) {
      setProfileError(err.message || 'Failed to update profile');
    } finally {
      setProfileLoading(false);
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError('');
    setPasswordSuccess('');

    if (newPassword !== confirmPassword) {
      setPasswordError('New passwords do not match');
      return;
    }

    if (newPassword.length < 6) {
      setPasswordError('New password must be at least 6 characters long');
      return;
    }

    setPasswordLoading(true);

    try {
      await changePassword(currentPassword, newPassword);
      setPasswordSuccess('Password changed successfully!');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      setPasswordError(err.message || 'Failed to change password');
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      router.push('/');
    } catch (err) {
      alert('Failed to logout');
    }
  };

  if (!user) {
    return null; // This shouldn't happen due to auth protection, but just in case
  }

  return (
    <div className="mx-auto grid max-w-4xl gap-8">
      <header className="surface-card space-y-3">
        <div className="grid gap-4 text-sm text-slate-300 sm:grid-cols-2">
          <div className="rounded-2xl border border-slate-800/70 bg-slate-900/60 px-4 py-3">
            <p className="text-xs uppercase tracking-wide text-slate-500">Account created</p>
            <p className="mt-1 font-semibold text-white">
              {new Date(user.created_at).toLocaleDateString()}
            </p>
          </div>
          <div className="rounded-2xl border border-slate-800/70 bg-slate-900/60 px-4 py-3">
            <p className="text-xs uppercase tracking-wide text-slate-500">Last login</p>
            <p className="mt-1 font-semibold text-white">
              {new Date(user.last_login).toLocaleString()}
            </p>
          </div>
        </div>
      </header>

      <section className="surface-card space-y-6">
        <div className="space-y-2">
          <h3 className="text-xl font-semibold text-white">Profile settings</h3>
        </div>

        {profileError && (
          <div className="rounded-2xl border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
            {profileError}
          </div>
        )}

        {profileSuccess && (
          <div className="rounded-2xl border border-emerald-500/40 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-200">
            {profileSuccess}
          </div>
        )}

        <form onSubmit={handleProfileUpdate} className="space-y-5">
          <div className="space-y-2">
            <label htmlFor="username" className="field-label">
              Username (Public)
            </label>
            <input
              type="text"
              className="input-field"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={profileLoading}
              minLength={3}
              maxLength={50}
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="email" className="field-label">
              Email address (Private)
            </label>
            <input
              type="email"
              className="input-field"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={profileLoading}
            />
          </div>

          <button type="submit" className="btn-primary w-full sm:w-auto" disabled={profileLoading}>
            {profileLoading ? 'Updating profile…' : 'Update profile'}
          </button>
        </form>
      </section>

      <section className="surface-card space-y-6">
        <div className="space-y-2">
          <h3 className="text-xl font-semibold text-white">Change password</h3>
        </div>

        {passwordError && (
          <div className="rounded-2xl border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
            {passwordError}
          </div>
        )}

        {passwordSuccess && (
          <div className="rounded-2xl border border-emerald-500/40 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-200">
            {passwordSuccess}
          </div>
        )}

        <form onSubmit={handlePasswordChange} className="space-y-5">
          <div className="space-y-2">
            <label htmlFor="currentPassword" className="field-label">
              Current password
            </label>
            <input
              type="password"
              className="input-field"
              id="currentPassword"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              required
              disabled={passwordLoading}
            />
          </div>

          <div className="grid gap-5 sm:grid-cols-2">
            <div className="space-y-2">
              <label htmlFor="newPassword" className="field-label">
                New password
              </label>
              <input
                type="password"
                className="input-field"
                id="newPassword"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                disabled={passwordLoading}
                minLength={6}
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="confirmPassword" className="field-label">
                Confirm new password
              </label>
              <input
                type="password"
                className="input-field"
                id="confirmPassword"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                disabled={passwordLoading}
              />
            </div>
          </div>

          <button type="submit" className="btn-primary w-full sm:w-auto" disabled={passwordLoading}>
            {passwordLoading ? 'Changing password…' : 'Change password'}
          </button>
        </form>
      </section>

      <div className="flex justify-end">
        <button
          onClick={handleLogout}
          className="btn-secondary whitespace-nowrap border-rose-400/60 text-rose-200 hover:border-rose-300 hover:text-rose-100"
        >
          Log out on this device
        </button>
      </div>
    </div>
  );
}
