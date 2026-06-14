// EPM Phase 2 — Login page wired to real FastAPI auth.
// POST /api/v1/auth/login sets a httpOnly JWT cookie server-side.
// GET /api/v1/auth/me (in _app.tsx) reads that cookie on subsequent navigations.
// No token stored in localStorage — cookie-only auth per handover spec.

import { createFileRoute, Link, redirect, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { Eye, EyeOff, Loader2 } from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import { useTheme } from "@/hooks/useTheme";
import type { User } from "@/types";

export const Route = createFileRoute("/login")({
  beforeLoad: () => {
    // Already authenticated → skip login page.
    if (useAuthStore.getState().user) {
      throw redirect({ to: "/dashboard" });
    }
  },
  component: LoginPage,
});

function LoginPage() {
  useTheme();
  const navigate = useNavigate();
  const setUser = useAuthStore((s) => s.setUser);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      // Step 1: POST credentials → FastAPI sets httpOnly cookie + returns user data.
      const res = await fetch("/api/v1/auth/login", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!res.ok) {
        const { detail } = await res.json().catch(() => ({ detail: "Login failed" }));
        setError(detail ?? "Invalid credentials");
        return;
      }

      const { data }: { data: User } = await res.json();

      // Step 2: Populate the Zustand store with the returned user profile.
      setUser(data);

      // Step 3: Navigate into the app. _app.tsx beforeLoad will fast-path.
      navigate({ to: "/dashboard" });
    } catch {
      setError("Cannot reach server. Check your connection.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-[var(--bg-canvas)]">
      {/* ── LEFT PANEL ─────────────────────────────────────────────────── */}
      <div
        className="md:w-[60%] min-h-[260px] md:min-h-screen relative flex items-center justify-center text-white px-8 py-10"
        style={{
          background: "linear-gradient(135deg, #646763 0%, #4a4d4b 50%, #3a3d3b 100%)",
        }}
      >
        {/* Lavender glow blob */}
        <div
          className="absolute pointer-events-none"
          style={{
            width: 400,
            height: 400,
            background: "radial-gradient(circle, rgba(188,189,250,0.20) 0%, transparent 70%)",
          }}
        />
        <div className="relative text-center">
          <div className="font-mono font-bold text-[#BCBDFA] text-[56px] md:text-[72px] leading-none">
            EPM
          </div>
          <div className="mt-4 text-[16px] md:text-[20px] text-white/85">
            Your Portfolio, Clearly.
          </div>
        </div>
        <div className="hidden md:block absolute bottom-6 left-8 text-[12px] text-white/40">
          Estate Portfolio Manager v2.0
        </div>
      </div>

      {/* ── RIGHT PANEL ────────────────────────────────────────────────── */}
      <div className="md:w-[40%] flex items-center justify-center px-6 md:px-10 py-10">
        <form onSubmit={onSubmit} className="w-full max-w-[360px]">
          <h1 className="text-[28px] font-bold text-[var(--text-primary)]">Welcome back</h1>
          <p className="text-[14px] text-[var(--text-secondary)] mt-2">Sign in to your portfolio</p>

          <div className="mt-8 space-y-4">
            <div>
              <label className="text-[12px] text-[var(--text-secondary)] uppercase tracking-wider font-semibold">
                Username
              </label>
              <input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
                required
                className="mt-1 w-full h-11 px-3 rounded-md bg-[var(--bg-surface)] border border-[var(--border)] text-[14px] text-[var(--text-primary)] focus-ring focus:border-[var(--accent-lavender)]"
              />
            </div>
            <div>
              <label className="text-[12px] text-[var(--text-secondary)] uppercase tracking-wider font-semibold">
                Password
              </label>
              <div className="relative mt-1">
                <input
                  type={show ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                  required
                  className="w-full h-11 px-3 pr-10 rounded-md bg-[var(--bg-surface)] border border-[var(--border)] text-[14px] text-[var(--text-primary)] focus-ring focus:border-[var(--accent-lavender)]"
                />
                <button
                  type="button"
                  onClick={() => setShow((s) => !s)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
                  aria-label="Toggle password visibility"
                >
                  {show ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="mt-6 w-full h-11 rounded-md bg-[var(--accent-lavender)] text-[#1A1A1A] font-semibold hover:opacity-90 disabled:opacity-60 flex items-center justify-center transition-opacity"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Sign In"}
          </button>

          {error && (
            <div className="mt-3 text-[13px] text-[var(--accent-red)] animate-in fade-in">
              {error}
            </div>
          )}

          {/* Dev-only bypass: skips login for UI review without a running backend */}
          {import.meta.env.DEV && (
            <div className="mt-6 text-center">
              <Link
                to="/dashboard"
                onClick={() => setUser({ id: 0, username: "dev", name: "Dev Mode", role: "admin" })}
                className="text-[12px] text-[var(--text-muted)] hover:text-[var(--accent-lavender)] underline underline-offset-2"
              >
                Skip to demo (dev only)
              </Link>
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
