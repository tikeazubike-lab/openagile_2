import { useState } from "react";
import { Link, useLocation, useNavigate } from "@tanstack/react-router";
import {
  LayoutDashboard,
  Briefcase,
  Building2,
  Coins,
  LineChart,
  ArrowLeftRight,
  ClipboardList,
  Eye,
  TrendingDown,
  Scale,
  Zap,
  Upload,
  Landmark,
  Users,
  Trash2,
  LogOut,
  Search,
} from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import { useUIStore } from "@/store/uiStore";
import { cn } from "@/lib/utils";

const MAIN = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/holdings", label: "Holdings", icon: Briefcase, badge: true },
  { to: "/companies", label: "Companies", icon: Building2 },
  { to: "/dividends", label: "Dividends", icon: Coins },
  { to: "/price-history", label: "Price History", icon: LineChart },
  { to: "/transactions", label: "Transactions", icon: ArrowLeftRight, badge: true },
  { to: "/registrars", label: "Registrars", icon: ClipboardList },
  { to: "/watchlist", label: "Watchlist", icon: Eye },
  { to: "/nav-history", label: "NAV History", icon: TrendingDown },
  { to: "/rebalancing", label: "Rebalancing", icon: Scale },
] as const;

const ADMIN = [
  { to: "/settings/price-entry", label: "Price Entry", icon: Zap, accent: true },
  { to: "/settings/data-import", label: "Data Import", icon: Upload },
  { to: "/settings/corporate-actions", label: "Corporate Actions", icon: Landmark },
  { to: "/settings/users", label: "User Management", icon: Users },
  { to: "/settings/deleted-records", label: "Deleted Records", icon: Trash2 },
] as const;

export function Sidebar() {
  const { user, isAdmin, clearUser } = useAuthStore();
  const sidebarOpen = useUIStore((s) => s.sidebarOpen);
  const setSidebarOpen = useUIStore((s) => s.setSidebarOpen);
  const location = useLocation();
  const path = location.pathname;
  const navigate = useNavigate();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleLogout = async () => {
    if (isLoggingOut) return;
    setIsLoggingOut(true);

    try {
      await fetch("/api/v1/auth/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch (_) {
      // Network failure — still log out locally
    } finally {
      clearUser();
      navigate({ to: "/login" });
    }
  };

  const initials = user?.name
    ? user.name
        .split(" ")
        .map((p) => p[0])
        .join("")
        .slice(0, 2)
        .toUpperCase()
    : "??";

  return (
    <>
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      <aside
        className={cn(
          "fixed md:sticky top-0 left-0 z-50 h-screen w-[220px] flex-col text-[var(--text-on-sidebar)] flex transition-transform duration-200",
          "border-r border-[var(--border)]",
          sidebarOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0",
        )}
        style={{
          background:
            "linear-gradient(180deg, var(--bg-sidebar) 0%, color-mix(in oklab, var(--bg-sidebar) 85%, black) 100%)",
        }}
      >
        {/* Brand */}
        <div className="px-4 h-14 flex flex-col justify-center">
          <div className="font-mono text-[20px] font-bold text-[var(--accent-lavender)] leading-none">
            EPM
          </div>
          <div className="text-[11px] text-white/60 mt-0.5">Estate Portfolio</div>
        </div>

        {/* Search */}
        <div className="px-3 mb-3">
          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-white/50" />
            <input
              placeholder="Search..."
              className="w-full h-8 pl-8 pr-10 rounded-md bg-white/10 border border-white/15 text-[13px] text-white placeholder:text-white/50 focus:outline-none focus:border-[var(--accent-lavender)]"
            />
            <span className="absolute right-2 top-1/2 -translate-y-1/2 text-[10px] font-mono text-white/50 bg-white/10 px-1.5 py-0.5 rounded">
              /
            </span>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto scrollbar-thin">
          <SectionLabel>Main</SectionLabel>
          <nav className="px-2 space-y-0.5">
            {MAIN.map((item) => (
              <NavItem
                key={item.to}
                to={item.to}
                label={item.label}
                Icon={item.icon}
                active={path === item.to || path.startsWith(item.to + "/")}
                badge={"badge" in item && item.badge ? "amber" : undefined}
              />
            ))}
          </nav>

          {isAdmin() && (
            <>
              <div className="my-3 mx-3 h-px bg-white/12" />
              <SectionLabel>Admin</SectionLabel>
              <nav className="px-2 space-y-0.5">
                {ADMIN.map((item) => (
                  <NavItem
                    key={item.to}
                    to={item.to}
                    label={item.label}
                    Icon={item.icon}
                    active={path === item.to}
                    accent={"accent" in item && item.accent}
                  />
                ))}
              </nav>
            </>
          )}
        </div>

        {/* User */}
        <div className="px-3 py-3 border-t border-white/10 flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-[var(--accent-lavender)] text-[#1A1A1A] font-mono text-[12px] font-semibold flex items-center justify-center">
            {initials}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-[13px] truncate">{user?.name ?? "Guest"}</div>
            <div className="text-[10px] text-white/50 capitalize">{user?.role ?? ""}</div>
          </div>
          <button
            onClick={handleLogout}
            className="p-1.5 rounded hover:bg-white/10 text-white/70"
            aria-label="Sign out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </aside>
    </>
  );
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="px-4 pt-3 pb-1.5 text-[10px] uppercase tracking-[0.1em] text-white/40">
      {children}
    </div>
  );
}

function NavItem({
  to,
  label,
  Icon,
  active,
  badge,
  accent,
}: {
  to: string;
  label: string;
  Icon: React.ComponentType<{ className?: string }>;
  active?: boolean;
  badge?: "amber" | "red";
  accent?: boolean;
}) {
  return (
    <Link
      to={to}
      className={cn(
        "flex items-center gap-3 h-10 px-3 rounded-lg text-[14px] transition-colors",
        active
          ? "bg-[var(--accent-lavender)] text-[#1A1A1A] font-medium"
          : "text-white/75 hover:text-white hover:bg-white/10",
        accent && !active && "text-[var(--accent-lavender)]",
      )}
    >
      <Icon className="w-5 h-5 shrink-0" />
      <span className="flex-1 truncate">{label}</span>
      {badge && (
        <span
          className={cn(
            "w-2 h-2 rounded-full",
            badge === "amber" ? "bg-[var(--accent-amber)]" : "bg-[var(--accent-red)]",
          )}
        />
      )}
    </Link>
  );
}
