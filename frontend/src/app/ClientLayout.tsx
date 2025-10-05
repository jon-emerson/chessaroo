'use client';

import { useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import Navigation from '../components/Navigation';
import Footer from '../components/Footer';
import { useAuth } from '../contexts/AuthContext';

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();
  const pathname = usePathname();

  // Public routes that don't require authentication
  const publicRoutes = ['/', '/login', '/register'];
  const isAdminRoute = pathname.startsWith('/admin');
  const isPublicRoute = publicRoutes.includes(pathname) || isAdminRoute;

  useEffect(() => {
    if (!isLoading && !isAuthenticated && !isPublicRoute) {
      router.replace('/login');
    }
  }, [isAuthenticated, isLoading, isPublicRoute, router]);

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
          <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '50vh' }}>
            <div className="text-center">
              <div className="spinner-border" role="status">
                <span className="visually-hidden">Redirecting...</span>
              </div>
              <p className="mt-2 text-muted">Redirecting to login…</p>
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
