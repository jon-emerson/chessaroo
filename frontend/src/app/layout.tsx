import type { Metadata } from 'next';
import 'bootstrap/dist/css/bootstrap.min.css';
import './globals.css';
import { AuthProvider } from '../contexts/AuthContext';
import ClientLayout from './ClientLayout';

export const metadata: Metadata = {
  title: 'BlunderLab - Multiplayer Chess',
  description: 'A multiplayer chess application with real-time collaboration',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <ClientLayout>{children}</ClientLayout>
        </AuthProvider>

        <script
          src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"
          async
        ></script>
      </body>
    </html>
  );
}