import type { AppProps } from "next/app";
import { useRouter } from "next/router";
import { useEffect } from "react";
import "@/styles/globals.css";
import { AuthProvider, useAuth } from "@/lib/auth";

// Public routes that don't require authentication
const PUBLIC_ROUTES = ["/login", "/forgot-password", "/reset-password"];

function AppContent({ Component, pageProps }: AppProps) {
  const router = useRouter();
  const { isAuthenticated, loading, checkAuth } = useAuth();

  useEffect(() => {
    const protectRoute = async () => {
      // Don't protect public routes
      if (PUBLIC_ROUTES.includes(router.pathname)) {
        return;
      }

      // Wait for auth to finish loading
      if (loading) {
        return;
      }

      // Check if authenticated
      if (!isAuthenticated) {
        const isValid = await checkAuth();
        if (!isValid) {
          router.push("/login");
        }
      }
    };

    protectRoute();
  }, [router.pathname, isAuthenticated, loading, checkAuth]);

  // Show loading state while checking auth
  if (loading && !PUBLIC_ROUTES.includes(router.pathname)) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-text-secondary">Loading...</div>
      </div>
    );
  }

  return <Component {...pageProps} />;
}

function App(props: AppProps) {
  return (
    <AuthProvider>
      <AppContent {...props} />
    </AuthProvider>
  );
}

export default App;

