export interface Stat {
  label: string;
  value: string;
}

export interface Subject {
  name: string;
  icon: string; // Lucide icon name — mapped in SubjectsSection
}

export interface Tutor {
  name: string;
  subjects: string[];
  rate_naira: number;
  bio: string;
  rating: number;
  image: string; // Absolute path: /assets/tutor_hub/images/tutor-N.jpg
}

export interface Step {
  step: number;
  title: string;
  description: string;
}

export interface Testimonial {
  name: string;
  role: string;
  text: string;
  rating: number;
}

export interface CtaLink {
  text: string;
  href: string; // Scroll anchor e.g. "#tutors" or "#how-it-works"
}

export interface LandingData {
  hero_title: string;
  hero_subtitle: string;
  cta_primary: CtaLink;
  cta_secondary: CtaLink;
  stats: Stat[];
  subjects: Subject[];
  featured_tutors: Tutor[];
  how_it_works: Step[];
  testimonials: Testimonial[];
}

// Frappe wraps all @whitelist responses in { message: T }
export interface FrappeResponse<T> {
  message: T;
}
