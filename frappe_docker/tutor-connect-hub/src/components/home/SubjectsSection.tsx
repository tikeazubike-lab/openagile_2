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
} from "lucide-react";

const subjects = [
  { name: "Mathematics", icon: Calculator, count: 45, color: "bg-blue-50 text-blue-600" },
  { name: "Physics", icon: Atom, count: 32, color: "bg-purple-50 text-purple-600" },
  { name: "Chemistry", icon: FlaskConical, count: 28, color: "bg-green-50 text-green-600" },
  { name: "Biology", icon: Leaf, count: 24, color: "bg-emerald-50 text-emerald-600" },
  { name: "English", icon: BookText, count: 38, color: "bg-amber-50 text-amber-600" },
  { name: "Computer Science", icon: Code2, count: 20, color: "bg-cyan-50 text-cyan-600" },
  { name: "Economics", icon: TrendingUp, count: 18, color: "bg-rose-50 text-rose-600" },
  { name: "Accounting", icon: DollarSign, count: 15, color: "bg-indigo-50 text-indigo-600" },
  { name: "French", icon: Languages, count: 12, color: "bg-teal-50 text-teal-600" },
  { name: "Geography", icon: Globe, count: 14, color: "bg-orange-50 text-orange-600" },
  { name: "History", icon: Clock, count: 16, color: "bg-pink-50 text-pink-600" },
  { name: "Yoruba", icon: MapPin, count: 10, color: "bg-lime-50 text-lime-600" },
];

export function SubjectsSection() {
  return (
    <section className="py-20 bg-white">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-foreground">Browse by Subject</h2>
          <p className="mt-3 text-muted-foreground max-w-2xl mx-auto">
            Explore tutors across a wide range of subjects. Whether you need help with
            exam prep or mastering new concepts, we have you covered.
          </p>
        </div>

        <div className="mt-12 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {subjects.map((subject) => (
            <button
              key={subject.name}
              className="group flex items-center gap-4 rounded-xl border border-border p-4 text-left transition-all hover:border-primary-300 hover:shadow-md"
            >
              <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${subject.color}`}>
                <subject.icon className="h-5 w-5" />
              </div>
              <div>
                <p className="font-medium text-foreground group-hover:text-primary-600 transition-colors">
                  {subject.name}
                </p>
                <p className="text-xs text-muted-foreground">{subject.count} tutors</p>
              </div>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
