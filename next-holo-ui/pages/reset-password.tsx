import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import { apiBaseFromEnv } from "@/lib/api";

export default function ResetPasswordPage() {
  const [token, setToken] = useState<string | null>(null);
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const { token: tokenParam } = router.query;
    if (tokenParam && typeof tokenParam === "string") {
      setToken(tokenParam);
    } else if (router.isReady) {
      setError("Invalid or missing reset token");
    }
  }, [router.query, router.isReady]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (newPassword.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    if (!token) {
      setError("Invalid reset token");
      return;
    }

    setLoading(true);

    try {
      const apiBase = apiBaseFromEnv();
      const response = await fetch(`${apiBase}/auth/reset-password`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ token, new_password: newPassword }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to reset password");
      }

      setSuccess(true);
      setTimeout(() => {
        router.push("/login");
      }, 2000);
    } catch (err: any) {
      setError(err.message || "Failed to reset password");
    } finally {
      setLoading(false);
    }
  };

  if (!token && router.isReady) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background px-4">
        <div className="w-full max-w-md">
          <div className="card p-8 shadow-lg">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-text-primary mb-4">Invalid Reset Link</h1>
              <p className="text-text-secondary mb-4">
                The password reset link is invalid or has expired.
              </p>
              <Link
                href="/forgot-password"
                className="btn-primary px-4 py-3 text-sm font-medium inline-block"
              >
                Request New Reset Link
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-md">
        <div className="card p-8 shadow-lg">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-text-primary mb-2">Reset Password</h1>
            <p className="text-text-secondary">Enter your new password</p>
          </div>

          {success ? (
            <div className="space-y-4">
              <div className="p-4 bg-green-50 border border-green-200 text-green-700 rounded-lg">
                <p className="font-medium">Password reset successfully!</p>
                <p className="text-sm mt-1">Redirecting to login page...</p>
              </div>
              <Link
                href="/login"
                className="block text-center btn-primary px-4 py-3 text-sm font-medium"
              >
                Go to Login
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="newPassword" className="block text-sm font-medium text-text-primary mb-2">
                  New Password
                </label>
                <input
                  id="newPassword"
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  minLength={6}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-text-primary focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
                  placeholder="••••••••"
                />
              </div>

              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-text-primary mb-2">
                  Confirm Password
                </label>
                <input
                  id="confirmPassword"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  minLength={6}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-text-primary focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
                  placeholder="••••••••"
                />
              </div>

              {error && (
                <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading || !token}
                className="w-full btn-primary px-4 py-3 text-sm font-medium disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {loading ? "Resetting..." : "Reset Password"}
              </button>

              <Link
                href="/login"
                className="block text-center text-sm text-primary hover:text-primary/80 transition-colors"
              >
                Back to Login
              </Link>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

