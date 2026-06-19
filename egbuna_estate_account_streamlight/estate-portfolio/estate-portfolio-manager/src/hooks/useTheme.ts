import { useEffect, useState } from "react";

export type ThemeMode = "system" | "dark";
type Resolved = "light" | "dark";

const STORAGE_KEY = "epm-theme";

function readStored(): ThemeMode {
  if (typeof window === "undefined") return "system";
  const v = localStorage.getItem(STORAGE_KEY);
  return v === "dark" ? "dark" : "system";
}

function systemPrefersDark(): boolean {
  if (typeof window === "undefined") return false;
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

function apply(resolved: Resolved) {
  if (typeof document === "undefined") return;
  document.documentElement.classList.toggle("dark", resolved === "dark");
}

export function useTheme() {
  const [theme, setTheme] = useState<ThemeMode>(() => readStored());
  const [resolvedTheme, setResolved] = useState<Resolved>(() =>
    readStored() === "dark" || (readStored() === "system" && systemPrefersDark())
      ? "dark"
      : "light",
  );

  useEffect(() => {
    const resolved: Resolved = theme === "dark" ? "dark" : systemPrefersDark() ? "dark" : "light";
    setResolved(resolved);
    apply(resolved);

    if (theme === "system") {
      const mq = window.matchMedia("(prefers-color-scheme: dark)");
      const handler = (e: MediaQueryListEvent) => {
        const r: Resolved = e.matches ? "dark" : "light";
        setResolved(r);
        apply(r);
      };
      mq.addEventListener("change", handler);
      return () => mq.removeEventListener("change", handler);
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => {
      const next: ThemeMode = prev === "system" ? "dark" : "system";
      if (next === "system") localStorage.setItem(STORAGE_KEY, "system");
      else localStorage.setItem(STORAGE_KEY, "dark");
      return next;
    });
  };

  return { theme, resolvedTheme, toggleTheme };
}
