'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiCall } from '../lib/api';

interface User {
  user_id: string;
  username: string;
  email: string;
  created_at: string;
  last_login: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (identifier: string, password: string) => Promise<void>;
  register: (email: string, password: string, username: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  updateProfile: (username: string, email: string) => Promise<void>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user;

  const checkAuth = async () => {
    try {
      const response = await apiCall('/api/auth/me');
      setUser(response.user);
    } catch (error) {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (identifier: string, password: string) => {
    const response = await apiCall('/api/auth/login', {
      method: 'POST',
      credentials: 'include',
      body: JSON.stringify({ identifier, password }),
    });
    setUser(response.user);
  };

  const register = async (email: string, password: string, username: string) => {
    const response = await apiCall('/api/auth/register', {
      method: 'POST',
      credentials: 'include',
      body: JSON.stringify({ email, password, username }),
    });
    setUser(response.user);
  };

  const logout = async () => {
    await apiCall('/api/auth/logout', {
      method: 'POST',
      credentials: 'include',
    });
    setUser(null);
  };

  const updateProfile = async (username: string, email: string) => {
    const response = await apiCall('/api/auth/update-profile', {
      method: 'PUT',
      credentials: 'include',
      body: JSON.stringify({ username, email }),
    });
    setUser(response.user);
  };

  const changePassword = async (currentPassword: string, newPassword: string) => {
    await apiCall('/api/auth/change-password', {
      method: 'PUT',
      credentials: 'include',
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    });
  };

  useEffect(() => {
    checkAuth();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        isLoading,
        login,
        register,
        logout,
        checkAuth,
        updateProfile,
        changePassword,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
