import { Link } from "react-router-dom";
import { GraduationCap, Mail, Phone, MapPin } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-border bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
          <div className="space-y-4">
            <Link to="/" className="flex items-center gap-2">
              <GraduationCap className="h-6 w-6 text-primary-500" />
              <span className="text-lg font-bold">
                Tutor<span className="text-primary-500">Connect</span>
              </span>
            </Link>
            <p className="text-sm text-muted-foreground">
              Connecting students with qualified tutors for personalized learning experiences.
            </p>
          </div>

          <div>
            <h4 className="mb-4 text-sm font-semibold">Platform</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><Link to="/register/student" className="hover:text-foreground">Find a Tutor</Link></li>
              <li><Link to="/register/tutor" className="hover:text-foreground">Become a Tutor</Link></li>
              <li><Link to="/login" className="hover:text-foreground">Log in</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="mb-4 text-sm font-semibold">Subjects</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>Mathematics</li>
              <li>Sciences</li>
              <li>Languages</li>
              <li>Business</li>
            </ul>
          </div>

          <div>
            <h4 className="mb-4 text-sm font-semibold">Contact</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li className="flex items-center gap-2">
                <Mail className="h-4 w-4" />
                support@tutorconnect.com
              </li>
              <li className="flex items-center gap-2">
                <Phone className="h-4 w-4" />
                +234 800 123 4567
              </li>
              <li className="flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                Lagos, Nigeria
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-10 border-t border-border pt-6 text-center text-sm text-muted-foreground">
          &copy; {new Date().getFullYear()} TutorConnect Hub. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
