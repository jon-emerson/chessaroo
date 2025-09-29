'use client';

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import Navigation from '../components/Navigation';
import Footer from '../components/Footer';
import { useAuth } from '../contexts/AuthContext';

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const pathname = usePathname();

  // Public routes that don't require authentication
  const publicRoutes = ['/login', '/register', '/admin'];
  const isPublicRoute = publicRoutes.includes(pathname);

  if (isLoading) {
    return (
      <>
        <div className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
          <div className="text-center">
            <div className="spinner-border" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
            <p className="mt-2">Loading Chessaroo...</p>
          </div>
        </div>
        <Footer />
      </>
    );
  }

  // If not authenticated and trying to access protected route
  if (!isAuthenticated && !isPublicRoute) {
    return (
      <>
        <Navigation />
        <main className="container mt-4">
          <div className="row justify-content-center">
            <div className="col-md-8 text-center">
              <div className="card">
                <div className="card-body">
                  <h2 className="card-title">♕ Welcome to Chessaroo</h2>
                  <p className="card-text">
                    Please log in or create an account to access the chess application.
                  </p>
                  <div className="d-flex gap-2 justify-content-center">
                    <a href="/login" className="btn btn-primary">
                      Login
                    </a>
                    <a href="/register" className="btn btn-outline-primary">
                      Sign Up
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Navigation />
      <main className="container mt-4">
        {children}
      </main>
      <Footer />
    </>
  );
}
