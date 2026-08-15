import { NavLink, Outlet, Navigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { Header } from "./Header";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Users,
  CreditCard,
  Settings,
  Calendar,
  BookOpen,
  Clock,
  Wallet,
  Search,
} from "lucide-react";

interface SidebarLink {
  to: string;
  label: string;
  icon: React.ReactNode;
  end?: boolean;
}

const ownerLinks: SidebarLink[] = [
  { to: "/owner", label: "Overview", icon: <LayoutDashboard className="h-4 w-4" />, end: true },
  { to: "/owner/tutors", label: "Tutors", icon: <Users className="h-4 w-4" /> },
  { to: "/owner/payments", label: "Payments", icon: <CreditCard className="h-4 w-4" /> },
  { to: "/owner/settings", label: "Settings", icon: <Settings className="h-4 w-4" /> },
];

const tutorLinks: SidebarLink[] = [
  { to: "/tutor", label: "Overview", icon: <LayoutDashboard className="h-4 w-4" />, end: true },
  { to: "/tutor/schedule", label: "Schedule", icon: <Calendar className="h-4 w-4" /> },
  { to: "/tutor/sessions", label: "Sessions", icon: <BookOpen className="h-4 w-4" /> },
  { to: "/tutor/earnings", label: "Earnings", icon: <Wallet className="h-4 w-4" /> },
];

const studentLinks: SidebarLink[] = [
  { to: "/student", label: "Overview", icon: <LayoutDashboard className="h-4 w-4" />, end: true },
  { to: "/student/browse", label: "Find Tutors", icon: <Search className="h-4 w-4" /> },
  { to: "/student/sessions", label: "My Sessions", icon: <Clock className="h-4 w-4" /> },
  { to: "/student/payments", label: "Payments", icon: <CreditCard className="h-4 w-4" /> },
];

function getLinks(isOwner: boolean, isTutor: boolean, isStudent: boolean): SidebarLink[] {
  if (isOwner) return ownerLinks;
  if (isTutor) return tutorLinks;
  if (isStudent) return studentLinks;
  return [];
}

function getSectionTitle(isOwner: boolean, isTutor: boolean): string {
  if (isOwner) return "Owner Dashboard";
  if (isTutor) return "Tutor Dashboard";
  return "Student Dashboard";
}

export function DashboardLayout() {
  const { isAuthenticated, isLoading, isOwner, isTutor, isStudent } = useAuth();

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-500 border-t-transparent" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  const links = getLinks(isOwner, isTutor, isStudent);
  const sectionTitle = getSectionTitle(isOwner, isTutor);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="mx-auto flex max-w-7xl">
        {/* Sidebar */}
        <aside className="hidden lg:block w-64 shrink-0 border-r border-border bg-white min-h-[calc(100vh-4rem)]">
          <div className="p-6">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              {sectionTitle}
            </h2>
          </div>
          <nav className="space-y-1 px-3">
            {links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                end={link.end}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary-50 text-primary-700"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  )
                }
              >
                {link.icon}
                {link.label}
              </NavLink>
            ))}
          </nav>
        </aside>

        {/* Mobile nav */}
        <div className="lg:hidden fixed bottom-0 left-0 right-0 z-40 border-t border-border bg-white">
          <nav className="flex justify-around py-2">
            {links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                end={link.end}
                className={({ isActive }) =>
                  cn(
                    "flex flex-col items-center gap-1 px-3 py-1 text-xs font-medium",
                    isActive ? "text-primary-600" : "text-muted-foreground"
                  )
                }
              >
                {link.icon}
                {link.label}
              </NavLink>
            ))}
          </nav>
        </div>

        {/* Main content */}
        <main className="flex-1 p-6 pb-24 lg:pb-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
