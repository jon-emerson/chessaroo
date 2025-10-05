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
      <div className="flex min-h-screen items-center justify-center bg-slate-950">
        <div className="flex flex-col items-center gap-4 text-center">
          <span className="h-12 w-12 animate-spin rounded-full border-2 border-slate-700/80 border-t-cyan-400" />
          <div>
            <p className="text-sm font-semibold tracking-wide text-slate-300">Calibrating BlunderLab</p>
            <p className="text-xs text-slate-500">Loading your chess intelligence toolkit…</p>
          </div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated && !isPublicRoute) {
    return (
      <div className="flex min-h-screen flex-col">
        <Navigation />
        <main className="flex flex-1 items-center justify-center">
          <div className="surface-card max-w-md text-center">
            <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-2 border-slate-700 border-t-cyan-400" />
            <h2 className="text-lg font-semibold text-white">Redirecting to login</h2>
            <p className="mt-2 text-sm text-slate-400">
              You need to be signed in to analyze your games. Hold tight for a second…
            </p>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col">
      <Navigation />
      <main className="mx-auto w-full max-w-7xl flex-1 px-6 pb-20 pt-12 sm:px-8 lg:px-10">
        {children}
      </main>
      <Footer />
    </div>
  );
}
