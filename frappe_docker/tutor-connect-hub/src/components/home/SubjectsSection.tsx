import {
  Calculator,
  Atom,
  FlaskConical,
  Leaf,
  BookText,
  Code2,
  TrendingUp,
  DollarSign,
  Globe,
  MapPin,
  Clock,
  Languages,
  ArrowRight,
} from "lucide-react";

const subjects = [
  { name: "Mathematics", icon: Calculator, count: 45, bg: "bg-accent-yellow-light", iconBg: "bg-accent-yellow", text: "text-foreground" },
  { name: "Physics", icon: Atom, count: 32, bg: "bg-accent-cyan-light", iconBg: "bg-accent-cyan", text: "text-foreground" },
  { name: "Chemistry", icon: FlaskConical, count: 28, bg: "bg-accent-mint-light", iconBg: "bg-accent-mint", text: "text-foreground" },
  { name: "Biology", icon: Leaf, count: 24, bg: "bg-accent-pink-light", iconBg: "bg-accent-pink", text: "text-foreground" },
  { name: "English", icon: BookText, count: 38, bg: "bg-accent-lavender-light", iconBg: "bg-accent-lavender", text: "text-foreground" },
  { name: "Computer Science", icon: Code2, count: 20, bg: "bg-accent-yellow-light", iconBg: "bg-secondary-400", text: "text-white" },
  { name: "Economics", icon: TrendingUp, count: 18, bg: "bg-accent-cyan-light", iconBg: "bg-primary-500", text: "text-white" },
  { name: "Accounting", icon: DollarSign, count: 15, bg: "bg-accent-mint-light", iconBg: "bg-secondary-500", text: "text-white" },
  { name: "French", icon: Languages, count: 12, bg: "bg-accent-pink-light", iconBg: "bg-primary-400", text: "text-white" },
  { name: "Geography", icon: Globe, count: 14, bg: "bg-accent-lavender-light", iconBg: "bg-accent-yellow", text: "text-foreground" },
  { name: "History", icon: Clock, count: 16, bg: "bg-accent-yellow-light", iconBg: "bg-accent-cyan", text: "text-foreground" },
  { name: "Yoruba", icon: MapPin, count: 10, bg: "bg-accent-cyan-light", iconBg: "bg-accent-pink", text: "text-foreground" },
];

export function SubjectsSection() {
  return (
    <section className="py-20 bg-white">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto">
          <span className="inline-flex items-center rounded-full bg-primary-100 px-4 py-1.5 text-sm font-extrabold text-primary-700 mb-4">
            Browse Subjects
          </span>
          <h2 className="text-3xl font-extrabold text-foreground sm:text-4xl">
            Explore Subjects With Expert Tutors
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Explore tutors across a wide range of subjects. Whether you need help with
            exam prep or mastering new concepts, we have you covered.
          </p>
        </div>

        <div className="mt-14 grid grid-cols-2 gap-5 sm:grid-cols-3 lg:grid-cols-4">
          {subjects.map((subject) => (
            <button
              key={subject.name}
              className={`group flex flex-col items-center gap-4 rounded-3xl ${subject.bg} p-6 text-center transition-all hover:-translate-y-1 hover:shadow-lg`}
            >
              <div className={`flex h-16 w-16 items-center justify-center rounded-2xl ${subject.iconBg} shadow-sm transition-transform group-hover:scale-110`}>
                <subject.icon className={`h-8 w-8 ${subject.text}`} />
              </div>
              <div>
                <p className="text-base font-extrabold text-foreground">
                  {subject.name}
                </p>
                <p className="text-sm text-muted-foreground">{subject.count} tutors</p>
              </div>
              <div className="mt-auto flex items-center text-sm font-extrabold text-primary-600 opacity-0 transition-opacity group-hover:opacity-100">
                Learn More <ArrowRight className="ml-1 h-4 w-4" />
              </div>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
