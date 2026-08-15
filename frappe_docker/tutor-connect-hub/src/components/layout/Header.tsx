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
import { GraduationCap, Menu, X, LogOut, LayoutDashboard, User, Mail, Phone } from "lucide-react";
import { getInitials } from "@/lib/utils";
import { useState } from "react";

export function Header() {
  const { isAuthenticated, user, isStudent, logout, getDefaultRoute } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  const dashboardRoute = getDefaultRoute();

  return (
    <header className="sticky top-0 z-40 w-full">
      {/* Top contact bar */}
      <div className="bg-primary-500 text-white">
        <div className="mx-auto flex h-9 max-w-7xl items-center justify-between px-4 text-xs sm:px-6 lg:px-8">
          <div className="flex items-center gap-4">
            <a href="mailto:support@tutorconnect.com" className="hidden items-center gap-1.5 hover:text-accent-yellow sm:flex">
              <Mail className="h-3.5 w-3.5" />
              support@tutorconnect.com
            </a>
            <a href="tel:+2348001234567" className="flex items-center gap-1.5 hover:text-accent-yellow">
              <Phone className="h-3.5 w-3.5" />
              +234 800 123 4567
            </a>
          </div>
          <div className="hidden items-center gap-4 sm:flex">
            <span className="font-semibold text-accent-yellow">Admission Open!</span>
            <span>Start learning today</span>
          </div>
        </div>
      </div>

      {/* Main nav */}
      <div className="border-b border-border bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/80">
        <div className="mx-auto flex h-18 max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
          <Link to="/" className="flex items-center gap-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-secondary-400 text-white shadow-md">
              <GraduationCap className="h-6 w-6" />
            </div>
            <span className="text-2xl font-extrabold text-foreground">
              Tutor<span className="text-primary-500">Connect</span>
            </span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden items-center gap-8 md:flex">
            <Link to="/" className="text-sm font-bold text-foreground hover:text-primary-500 transition-colors">
              Home
            </Link>
            {isStudent && (
              <Link to="/student/browse" className="text-sm font-bold text-muted-foreground hover:text-primary-500 transition-colors">
                Find Tutors
              </Link>
            )}
            {isAuthenticated && (
              <Link to={dashboardRoute} className="text-sm font-bold text-muted-foreground hover:text-primary-500 transition-colors">
                Dashboard
              </Link>
            )}
          </nav>

          <div className="hidden items-center gap-3 md:flex">
            {isAuthenticated ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="flex items-center gap-2 rounded-full px-3 py-1.5 hover:bg-primary-50 transition-colors">
                    <Avatar className="h-9 w-9 border-2 border-primary-200">
                      <AvatarFallback className="text-xs font-bold bg-primary-100 text-primary-700">
                        {getInitials(user?.full_name || user?.email || "U")}
                      </AvatarFallback>
                    </Avatar>
                    <span className="text-sm font-bold">{user?.full_name || user?.email}</span>
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48 rounded-2xl">
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
            className="md:hidden p-2 rounded-xl hover:bg-primary-50"
            onClick={() => setMobileOpen(!mobileOpen)}
          >
            {mobileOpen ? <X className="h-6 w-6 text-primary-500" /> : <Menu className="h-6 w-6 text-primary-500" />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden border-b border-border bg-white px-4 py-4 space-y-3 rounded-b-3xl shadow-lg">
          <Link to="/" className="block py-2 text-base font-bold text-foreground" onClick={() => setMobileOpen(false)}>
            Home
          </Link>
          {isStudent && (
            <Link to="/student/browse" className="block py-2 text-base font-bold text-muted-foreground" onClick={() => setMobileOpen(false)}>
              Find Tutors
            </Link>
          )}
          {isAuthenticated ? (
            <>
              <Link to={dashboardRoute} className="block py-2 text-base font-bold text-muted-foreground" onClick={() => setMobileOpen(false)}>
                Dashboard
              </Link>
              <button onClick={handleLogout} className="block py-2 text-base font-bold text-destructive">
                Log out
              </button>
            </>
          ) : (
            <div className="flex flex-col gap-2 pt-2">
              <Button variant="outline" className="w-full" onClick={() => { navigate("/login"); setMobileOpen(false); }}>
                Log in
              </Button>
              <Button className="w-full" onClick={() => { navigate("/register/student"); setMobileOpen(false); }}>
                Get Started
              </Button>
            </div>
          )}
        </div>
      )}
    </header>
  );
}
