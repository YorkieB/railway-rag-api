/**
 * Simplified Authentication Context
 * Manages user authentication state and token storage
 */

import { createContext, useContext, useState, useEffect, ReactNode } from "react";

export interface User {
  user_id: string;
  email: string;
  username: string;
  is_admin: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = "auth_token";
const USER_KEY = "auth_user";
const REMEMBER_ME_KEY = "auth_remember_me";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Load auth state from storage on mount (non-blocking)
  useEffect(() => {
    const initAuth = () => {
      try {
        const rememberMe = localStorage.getItem(REMEMBER_ME_KEY) === "true";
        const storage = rememberMe ? localStorage : sessionStorage;
        
        const storedToken = storage.getItem(TOKEN_KEY);
        const storedUser = storage.getItem(USER_KEY);

        if (storedToken && storedUser) {
          setToken(storedToken);
          try {
            const userData = JSON.parse(storedUser);
            setUser(userData);
          } catch (e) {
            console.error("Failed to parse stored user data:", e);
            clearAuth();
          }
        }
      } catch (e) {
        console.error("Error initializing auth:", e);
        clearAuth();
      }
      // Don't block rendering - set loading to false immediately
      setLoading(false);
    };

    // Initialize immediately without blocking
    initAuth();
  }, []);

  const clearAuth = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem(REMEMBER_ME_KEY);
    sessionStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(USER_KEY);
    setToken(null);
    setUser(null);
  };

  const logout = () => {
    clearAuth();
    if (typeof window !== "undefined") {
      window.location.href = "/";
    }
  };

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!user && !!token,
    isAdmin: user?.is_admin || false,
    logout,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
