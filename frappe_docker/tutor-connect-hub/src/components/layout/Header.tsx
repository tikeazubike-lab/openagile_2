import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { GraduationCap, Menu, X, LogOut, LayoutDashboard, User } from "lucide-react";
import { getInitials } from "@/lib/utils";
import { useState } from "react";

export function Header() {
  const { isAuthenticated, user, isOwner, isTutor, isStudent, logout, getDefaultRoute } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  const dashboardRoute = getDefaultRoute();

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link to="/" className="flex items-center gap-2">
          <GraduationCap className="h-7 w-7 text-primary-500" />
          <span className="text-xl font-bold text-foreground">
            Tutor<span className="text-primary-500">Connect</span>
          </span>
        </Link>

        {/* Desktop nav */}
        <nav className="hidden md:flex items-center gap-6">
          <Link to="/" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            Home
          </Link>
          {isStudent && (
            <Link to="/student/browse" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
              Find Tutors
            </Link>
          )}
          {isAuthenticated && (
            <Link to={dashboardRoute} className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
              Dashboard
            </Link>
          )}
        </nav>

        <div className="hidden md:flex items-center gap-3">
          {isAuthenticated ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex items-center gap-2 rounded-lg px-2 py-1 hover:bg-muted transition-colors">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="text-xs bg-primary-100 text-primary-700">
                      {getInitials(user?.full_name || user?.email || "U")}
                    </AvatarFallback>
                  </Avatar>
                  <span className="text-sm font-medium">{user?.full_name || user?.email}</span>
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuItem onClick={() => navigate(dashboardRoute)}>
                  <LayoutDashboard className="mr-2 h-4 w-4" />
                  Dashboard
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigate(`${dashboardRoute}/profile`)}>
                  <User className="mr-2 h-4 w-4" />
                  Profile
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="text-destructive">
                  <LogOut className="mr-2 h-4 w-4" />
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <>
              <Button variant="ghost" onClick={() => navigate("/login")}>
                Log in
              </Button>
              <Button onClick={() => navigate("/register/student")}>
                Get Started
              </Button>
            </>
          )}
        </div>

        {/* Mobile menu button */}
        <button
          className="md:hidden p-2 rounded-lg hover:bg-muted"
          onClick={() => setMobileOpen(!mobileOpen)}
        >
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden border-t border-border bg-white px-4 py-4 space-y-3">
          <Link to="/" className="block py-2 text-sm font-medium" onClick={() => setMobileOpen(false)}>
            Home
          </Link>
          {isStudent && (
            <Link to="/student/browse" className="block py-2 text-sm font-medium" onClick={() => setMobileOpen(false)}>
              Find Tutors
            </Link>
          )}
          {isAuthenticated ? (
            <>
              <Link to={dashboardRoute} className="block py-2 text-sm font-medium" onClick={() => setMobileOpen(false)}>
                Dashboard
              </Link>
              <button onClick={handleLogout} className="block py-2 text-sm font-medium text-destructive">
                Log out
              </button>
            </>
          ) : (
            <div className="flex gap-2 pt-2">
              <Button variant="outline" className="flex-1" onClick={() => { navigate("/login"); setMobileOpen(false); }}>
                Log in
              </Button>
              <Button className="flex-1" onClick={() => { navigate("/register/student"); setMobileOpen(false); }}>
                Get Started
              </Button>
            </div>
          )}
        </div>
      )}
    </header>
  );
}
