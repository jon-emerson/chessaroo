'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '../contexts/AuthContext';

export default function Navigation() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();


  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
      <div className="container">
        <Link className="navbar-brand" href="/">
          ♕ BlunderLab
        </Link>

        <div className="navbar-nav ms-auto">
          {isAuthenticated ? (
            <>
              <Link className="nav-link" href="/settings">
                {user?.username}
              </Link>
            </>
          ) : (
            <>
              <Link className="nav-link" href="/login">
                Login
              </Link>
              <Link className="nav-link" href="/register">
                Sign Up
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
