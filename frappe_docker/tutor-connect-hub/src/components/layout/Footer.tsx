import { Link } from "react-router-dom";
import { GraduationCap, Mail, Phone, MapPin } from "lucide-react";
import { GrassEdge } from "@/components/ui/doodles";

const socials = [
  { label: "f", name: "Facebook", href: "https://facebook.com" },
  { label: "X", name: "Twitter", href: "https://twitter.com" },
  { label: "Ig", name: "Instagram", href: "https://instagram.com" },
];

export function Footer() {
  return (
    <footer className="relative bg-primary-800 text-white">
      <div className="absolute bottom-0 left-0 right-0">
        <GrassEdge />
      </div>

      <div className="mx-auto max-w-7xl px-4 pb-20 pt-14 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-10 md:grid-cols-2 lg:grid-cols-4">
          <div className="space-y-4">
            <Link to="/" className="flex items-center gap-2">
              <div className="flex h-11 w-11 items-center justify-center rounded-full bg-secondary-400 text-white shadow-md">
                <GraduationCap className="h-6 w-6" />
              </div>
              <span className="text-2xl font-black">
                Tutor<span className="text-accent-yellow">Connect</span>
              </span>
            </Link>
            <p className="text-sm leading-relaxed text-primary-200">
              Connecting students with qualified tutors for personalized learning experiences that are fun, flexible, and effective.
            </p>
            <div className="flex gap-3 pt-1">
              {socials.map((s) => (
                <a
                  key={s.name}
                  href={s.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={s.name}
                  className="flex h-9 w-9 items-center justify-center rounded-full bg-primary-700 text-xs font-black text-white transition-colors hover:bg-secondary-400"
                >
                  {s.label}
                </a>
              ))}
            </div>
          </div>

          <div>
            <h4 className="mb-5 text-base font-black text-accent-yellow">Platform</h4>
            <ul className="space-y-3 text-sm font-semibold text-primary-100">
              <li><Link to="/register/student" className="hover:text-white transition-colors">Find a Tutor</Link></li>
              <li><Link to="/register/tutor" className="hover:text-white transition-colors">Become a Tutor</Link></li>
              <li><Link to="/login" className="hover:text-white transition-colors">Log in</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="mb-5 text-base font-black text-accent-yellow">Subjects</h4>
            <ul className="space-y-3 text-sm font-semibold text-primary-100">
              <li>Mathematics</li>
              <li>Sciences</li>
              <li>Languages</li>
              <li>Business</li>
            </ul>
          </div>

          <div>
            <h4 className="mb-5 text-base font-black text-accent-yellow">Contact</h4>
            <ul className="space-y-3 text-sm font-semibold text-primary-100">
              <li className="flex items-center gap-2">
                <Mail className="h-4 w-4 text-accent-yellow" />
                support@tutorconnect.com
              </li>
              <li className="flex items-center gap-2">
                <Phone className="h-4 w-4 text-accent-yellow" />
                +234 800 123 4567
              </li>
              <li className="flex items-center gap-2">
                <MapPin className="h-4 w-4 text-accent-yellow" />
                Lagos, Nigeria
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 border-t border-primary-700 pt-6 text-center text-sm font-semibold text-primary-200">
          &copy; {new Date().getFullYear()} TutorConnect Hub. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
