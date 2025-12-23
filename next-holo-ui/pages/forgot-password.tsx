import { useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import { apiBaseFromEnv } from "@/lib/api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const apiBase = apiBaseFromEnv();
      const response = await fetch(`${apiBase}/auth/forgot-password`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to send reset email");
      }

      setSuccess(true);
    } catch (err: any) {
      setError(err.message || "Failed to process request");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-md">
        <div className="card p-8 shadow-lg">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-text-primary mb-2">Forgot Password</h1>
            <p className="text-text-secondary">Enter your email to receive a password reset link</p>
          </div>

          {success ? (
            <div className="space-y-4">
              <div className="p-4 bg-green-50 border border-green-200 text-green-700 rounded-lg">
                <p className="font-medium">Reset link sent!</p>
                <p className="text-sm mt-1">
                  If an account with that email exists, a password reset link has been sent.
                  Please check your email and click the link to reset your password.
                </p>
              </div>
              <Link
                href="/login"
                className="block text-center btn-primary px-4 py-3 text-sm font-medium"
              >
                Back to Login
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-text-primary mb-2">
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-text-primary focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
                  placeholder="you@example.com"
                />
              </div>

              {error && (
                <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full btn-primary px-4 py-3 text-sm font-medium disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {loading ? "Sending..." : "Send Reset Link"}
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

