// Scroll-anchor navigation — no react-router, no page reloads.
// All hrefs point to #section-id anchors defined in App.tsx.

export default function Header() {
  const handleAnchorClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    if (href.startsWith("#")) {
      e.preventDefault();
      document.querySelector(href)?.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        <a href="#home" className="flex items-center gap-2 font-bold text-xl font-serif">
          <span className="text-primary">Tutor</span>Hub
        </a>

        <nav className="hidden md:flex items-center gap-6 text-sm font-medium">
          {[
            { label: "Find a Tutor", href: "#tutors" },
            { label: "Subjects", href: "#subjects" },
            { label: "How It Works", href: "#how-it-works" },
          ].map(({ label, href }) => (
            <a
              key={href}
              href={href}
              onClick={(e) => handleAnchorClick(e, href)}
              className="text-muted-foreground transition-colors hover:text-foreground"
            >
              {label}
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          <a
            href="/login"
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            Log In
          </a>
          <a
            href="#tutors"
            onClick={(e) => handleAnchorClick(e, "#tutors")}
            className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground shadow hover:bg-primary/90 transition-colors"
          >
            Get Started
          </a>
        </div>
      </div>
    </header>
  );
}
