import { useLocation, Link } from "@tanstack/react-router";
import { Bell, ClipboardCheck, Menu, Moon, Sun } from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import { useUIStore } from "@/store/uiStore";
import { useTheme } from "@/hooks/useTheme";
import { cn } from "@/lib/utils";
import { useActionItems } from "@/api/queries";
import { useState, useRef, useEffect } from "react";

const TITLES: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/holdings": "Holdings",
  "/companies": "Companies",
  "/dividends": "Dividends",
  "/price-history": "Price History",
  "/transactions": "Transactions",
  "/registrars": "Registrars",
  "/watchlist": "Watchlist",
  "/nav-history": "NAV History",
  "/rebalancing": "Rebalancing",
  "/settings/price-entry": "Price Entry",
  "/settings/data-import": "Data Import",
  "/settings/data-upload": "Data Upload",
  "/settings/corporate-actions": "Corporate Actions",
  "/settings/users": "User Management",
  "/settings/deleted-records": "Deleted Records",
};

export function Navbar() {
  const location = useLocation();
  const pathname = location.pathname;
  const title = TITLES[pathname] ?? "Estate Portfolio";
  const { isAdmin, user } = useAuthStore();
  const { toggleSidebar } = useUIStore();
  const { resolvedTheme, toggleTheme } = useTheme();

  const { data: actionItemsData } = useActionItems();
  const actionItems = actionItemsData?.items || [];

  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsNotificationsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const initials = user?.name
    ? user.name
        .split(" ")
        .map((p) => p[0])
        .join("")
        .slice(0, 2)
        .toUpperCase()
    : "??";

  const isDashboard = pathname === "/dashboard" || pathname === "/_app/dashboard";

  return (
    <header className="sticky top-0 z-30 h-14 px-4 md:px-6 bg-[var(--bg-surface)] border-b border-[var(--border)] flex items-center gap-3">
      <button
        onClick={toggleSidebar}
        className="md:hidden p-1.5 rounded-md hover:bg-[var(--bg-subtle)]"
        aria-label="Open menu"
      >
        <Menu className="w-5 h-5 text-[var(--text-secondary)]" />
      </button>

      <h1 className="text-[18px] font-semibold text-[var(--text-primary)]">{title}</h1>

      <div className="ml-auto flex items-center gap-3">
        <button
          onClick={toggleTheme}
          className="w-8 h-8 rounded-md hover:bg-[var(--bg-subtle)] flex items-center justify-center transition-colors"
          title={resolvedTheme === "dark" ? "Return to system theme" : "Switch to dark mode"}
        >
          {resolvedTheme === "dark" ? (
            <Sun className="w-[18px] h-[18px] text-[var(--accent-gold)] transition-opacity duration-150" />
          ) : (
            <Moon className="w-[18px] h-[18px] text-[var(--text-secondary)] transition-opacity duration-150" />
          )}
        </button>

        {isAdmin() && (
          <>
          <a
            href="/test-checklist"
            target="_blank"
            rel="noopener noreferrer"
            className="w-8 h-8 rounded-md hover:bg-[var(--bg-subtle)] flex items-center justify-center"
            title="Pre-Merge Checklist"
          >
            <ClipboardCheck className="w-[18px] h-[18px] text-[var(--text-muted)]" />
          </a>
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
              className="relative w-8 h-8 rounded-md hover:bg-[var(--bg-subtle)] flex items-center justify-center"
            >
              <Bell className="w-5 h-5 text-[var(--text-muted)]" />
              {actionItems.length > 0 && (
                <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-[var(--accent-amber)]" />
              )}
            </button>
            {isNotificationsOpen && (
              <div className="absolute right-0 mt-2 w-80 bg-[var(--bg-surface)] border border-[var(--border)] rounded-md shadow-lg overflow-hidden z-50">
                <div className="px-4 py-2 bg-[var(--bg-subtle)] border-b border-[var(--border)] font-semibold text-[14px]">
                  Action Items ({actionItems.length})
                </div>
                <div className="max-h-64 overflow-y-auto">
                  {actionItems.length === 0 ? (
                    <div className="p-4 text-center text-[13px] text-[var(--text-muted)]">
                      No action items. You're all caught up!
                    </div>
                  ) : (
                    actionItems.map((item) => (
                      <Link
                        key={item.id}
                        to={item.link}
                        onClick={() => setIsNotificationsOpen(false)}
                        className="block px-4 py-3 hover:bg-[var(--bg-subtle)] border-b border-[var(--border)] last:border-b-0"
                      >
                        <div className="text-[13px] font-medium text-[var(--text-primary)]">
                          {item.title}
                        </div>
                        <div className="text-[12px] text-[var(--text-muted)] mt-1">
                          {item.description}
                        </div>
                      </Link>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
            </> )}

        <div className="w-8 h-8 rounded-full bg-[var(--accent-lavender)] text-[#1A1A1A] font-mono text-[12px] font-semibold flex items-center justify-center">
          {initials}
        </div>
      </div>
    </header>
  );
}
