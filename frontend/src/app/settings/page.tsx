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
      router.push('/login');
    } catch (err) {
      alert('Failed to logout');
    }
  };

  if (!user) {
    return null; // This shouldn't happen due to auth protection, but just in case
  }

  return (
    <div className="row justify-content-center">
      <div className="col-md-8">
        <h2>⚙️ Account Settings</h2>
        <p className="text-muted">Manage your account information and preferences</p>

        {/* Account Information */}
        <div className="card mb-4">
          <div className="card-header">
            <h5 className="mb-0">Account Information</h5>
          </div>
          <div className="card-body">
            <div className="row">
              <div className="col-md-6">
                <p><strong>Account Created:</strong> {new Date(user.created_at).toLocaleDateString()}</p>
              </div>
              <div className="col-md-6">
                <p><strong>Last Login:</strong> {new Date(user.last_login).toLocaleDateString()}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Profile Settings */}
        <div className="card mb-4">
          <div className="card-header">
            <h5 className="mb-0">Profile Settings</h5>
          </div>
          <div className="card-body">
            <div className="alert alert-info">
              <small>
                <strong>Note:</strong> Your username is how other users will see you in the application.
                Your email address is kept private and used only for login.
              </small>
            </div>

            {profileError && (
              <div className="alert alert-danger" role="alert">
                {profileError}
              </div>
            )}

            {profileSuccess && (
              <div className="alert alert-success" role="alert">
                {profileSuccess}
              </div>
            )}

            <form onSubmit={handleProfileUpdate}>
              <div className="mb-3">
                <label htmlFor="username" className="form-label">
                  Username <span className="text-muted">(visible to other users)</span>
                </label>
                <input
                  type="text"
                  className="form-control"
                  id="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  disabled={profileLoading}
                  minLength={3}
                  maxLength={50}
                />
              </div>

              <div className="mb-3">
                <label htmlFor="email" className="form-label">
                  Email Address <span className="text-muted">(private, for login only)</span>
                </label>
                <input
                  type="email"
                  className="form-control"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  disabled={profileLoading}
                />
              </div>

              <button
                type="submit"
                className="btn btn-primary"
                disabled={profileLoading}
              >
                {profileLoading ? (
                  <>
                    <span
                      className="spinner-border spinner-border-sm me-2"
                      role="status"
                      aria-hidden="true"
                    ></span>
                    Updating...
                  </>
                ) : (
                  'Update Profile'
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Change Password */}
        <div className="card mb-4">
          <div className="card-header">
            <h5 className="mb-0">Change Password</h5>
          </div>
          <div className="card-body">
            {passwordError && (
              <div className="alert alert-danger" role="alert">
                {passwordError}
              </div>
            )}

            {passwordSuccess && (
              <div className="alert alert-success" role="alert">
                {passwordSuccess}
              </div>
            )}

            <form onSubmit={handlePasswordChange}>
              <div className="mb-3">
                <label htmlFor="currentPassword" className="form-label">
                  Current Password
                </label>
                <input
                  type="password"
                  className="form-control"
                  id="currentPassword"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  required
                  disabled={passwordLoading}
                />
              </div>

              <div className="mb-3">
                <label htmlFor="newPassword" className="form-label">
                  New Password
                </label>
                <input
                  type="password"
                  className="form-control"
                  id="newPassword"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  disabled={passwordLoading}
                  minLength={6}
                />
              </div>

              <div className="mb-3">
                <label htmlFor="confirmPassword" className="form-label">
                  Confirm New Password
                </label>
                <input
                  type="password"
                  className="form-control"
                  id="confirmPassword"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  disabled={passwordLoading}
                />
              </div>

              <button
                type="submit"
                className="btn btn-warning"
                disabled={passwordLoading}
              >
                {passwordLoading ? (
                  <>
                    <span
                      className="spinner-border spinner-border-sm me-2"
                      role="status"
                      aria-hidden="true"
                    ></span>
                    Changing Password...
                  </>
                ) : (
                  'Change Password'
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Logout Section */}
        <div className="card mb-4">
          <div className="card-header">
            <h5 className="mb-0">Session</h5>
          </div>
          <div className="card-body">
            <p className="text-muted mb-3">
              Log out of your account. You'll need to sign in again to access BlunderLab.
            </p>
            <button
              onClick={handleLogout}
              className="btn btn-outline-danger"
            >
              Log Out
            </button>
          </div>
        </div>

        {/* Back to Games */}
        <div className="text-center">
          <button
            onClick={() => router.push('/')}
            className="btn btn-outline-secondary"
          >
            ← Back to Games
          </button>
        </div>
      </div>
    </div>
  );
}