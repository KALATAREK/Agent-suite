"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import GoogleLoginButton from "@/components/GoogleLoginButton";
import { apiFetch } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isRegister, setIsRegister] = useState(false);

  const isValidEmail = (email: string) =>
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  // 🔥 AUTO LOGIN
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) router.replace("/");
  }, [router]);

  // =========================
  // 🔐 LOGIN / REGISTER CORE
  // =========================
  const handleAuth = async () => {
    if (loading) return;

    const cleanEmail = email.trim();

    if (!cleanEmail || !password.trim()) {
      setError("Fill all fields");
      return;
    }

    if (!isValidEmail(cleanEmail)) {
      setError("Invalid email format");
      return;
    }

    if (isRegister && password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const endpoint = isRegister ? "/auth/register" : "/auth/login";

      const data = await apiFetch(endpoint, {
        method: "POST",
        body: JSON.stringify({
          email: cleanEmail,
          password,
        }),
      });

      if (!data?.access_token) {
        throw new Error("Invalid server response");
      }

      localStorage.setItem("token", data.access_token);

      if (data.refresh_token) {
        localStorage.setItem("refresh_token", data.refresh_token);
      }

      if (data.user) {
        localStorage.setItem("user", JSON.stringify(data.user));
      }

      router.replace("/");
    } catch (err: any) {
      setError(err?.message || (isRegister ? "Register failed" : "Login failed"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden px-4">

      {/* BACKGROUND */}
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(59,130,246,0.14),transparent_32%),radial-gradient(circle_at_80%_25%,rgba(168,85,247,0.14),transparent_30%),radial-gradient(circle_at_50%_100%,rgba(59,130,246,0.08),transparent_35%)]" />

      <div className="relative z-10 w-full max-w-[460px]">
        <div className="rounded-[28px] border border-white/10 bg-white/[0.04] p-8 shadow-[0_20px_80px_rgba(0,0,0,0.45)] backdrop-blur-2xl">

          {/* LOGO */}
          <div className="mb-8 text-center">
            <div className="mb-4 inline-flex h-14 w-14 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-lg font-semibold shadow-[0_0_30px_rgba(59,130,246,0.15)]">
              A
            </div>

            <h1 className="text-3xl font-semibold tracking-tight text-white">
              AgentSuite
            </h1>
            <p className="mt-2 text-sm text-white/45">
              {isRegister ? "Create your account" : "Sign in to your AI workspace"}
            </p>
          </div>

          {/* GOOGLE (fallback safe) */}
          <div className="mb-5 flex justify-center">
            <GoogleLoginButton onSuccess={() => router.replace("/")} />
          </div>

          {/* DIVIDER */}
          <div className="mb-5 flex items-center gap-3">
            <div className="h-px flex-1 bg-white/10" />
            <span className="text-xs uppercase tracking-[0.2em] text-white/30">
              or
            </span>
            <div className="h-px flex-1 bg-white/10" />
          </div>

          {/* FORM */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleAuth();
            }}
            className="space-y-4"
          >
            <input
              autoFocus
              type="email"
              autoComplete="email"
              placeholder="you@company.com"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                setError("");
              }}
              disabled={loading}
              className="w-full rounded-2xl border border-white/10 bg-black/25 px-4 py-3 text-sm text-white placeholder:text-white/25 outline-none focus:border-blue-500/40"
            />

            <input
              type="password"
              autoComplete="current-password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                setError("");
              }}
              disabled={loading}
              className="w-full rounded-2xl border border-white/10 bg-black/25 px-4 py-3 text-sm text-white placeholder:text-white/25 outline-none focus:border-purple-500/40"
            />

            {error && (
              <div className="rounded-xl bg-red-500/10 px-4 py-2 text-sm text-red-300">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-2xl bg-gradient-to-r from-blue-500 to-purple-500 py-3 text-sm font-semibold text-white transition hover:scale-[0.99] disabled:opacity-50"
            >
              {loading
                ? "Processing..."
                : isRegister
                ? "Create account"
                : "Sign in"}
            </button>
          </form>

          {/* TOGGLE */}
          <div className="mt-4 text-center text-sm text-white/40">
            {isRegister ? "Already have an account?" : "No account yet?"}

            <button
              onClick={() => {
                setIsRegister(!isRegister);
                setError("");
              }}
              className="ml-2 text-blue-400 hover:text-blue-300"
            >
              {isRegister ? "Sign in" : "Register"}
            </button>
          </div>

          {/* FOOTER */}
          <div className="mt-6 text-center text-xs text-white/28">
            Secure access • JWT auth • Session-based workspace
          </div>
        </div>
      </div>
    </main>
  );
}