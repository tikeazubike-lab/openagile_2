export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t bg-muted/40">
      <div className="container py-10 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
        <p className="font-semibold text-foreground font-serif">
          <span className="text-primary">Tutor</span>Hub
        </p>

        <nav className="flex gap-6">
          {["About", "Contact", "Privacy Policy", "Terms"].map((label) => (
            <a
              key={label}
              href="#"
              className="hover:text-foreground transition-colors"
            >
              {label}
            </a>
          ))}
        </nav>

        <p>© {year} TutorHub. All rights reserved.</p>
      </div>
    </footer>
  );
}
