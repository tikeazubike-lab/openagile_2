import { useState } from "react";
import { useTutors } from "@/hooks/useTutors";
import { TutorCard } from "./TutorCard";
import { SUBJECTS } from "@/lib/constants";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";

export function TutorList() {
  const [subject, setSubject] = useState<string>("");
  const [search, setSearch] = useState("");
  const { data: tutors, isLoading, error } = useTutors({ active: true });

  const filtered = tutors?.filter((t) => {
    const matchesSubject = !subject || t.subjects?.toLowerCase().includes(subject.toLowerCase());
    const matchesSearch =
      !search ||
      t.full_name.toLowerCase().includes(search.toLowerCase()) ||
      t.subjects?.toLowerCase().includes(search.toLowerCase());
    return matchesSubject && matchesSearch;
  });

  return (
    <div>
      <div className="flex flex-col sm:flex-row gap-4 mb-8">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search by name or subject..."
            className="pl-9"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <Select value={subject} onValueChange={setSubject}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="All Subjects" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Subjects</SelectItem>
            {SUBJECTS.map((s) => (
              <SelectItem key={s} value={s}>
                {s}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {isLoading && (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-64 rounded-xl bg-muted animate-pulse" />
          ))}
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-destructive/20 bg-destructive/5 p-4 text-center text-sm text-destructive">
          Failed to load tutors. Please try again later.
        </div>
      )}

      {filtered && filtered.length === 0 && (
        <div className="rounded-lg border border-border bg-gray-50 p-12 text-center">
          <p className="text-muted-foreground">No tutors found matching your criteria.</p>
        </div>
      )}

      {filtered && filtered.length > 0 && (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((tutor) => (
            <TutorCard key={tutor.name} tutor={tutor} />
          ))}
        </div>
      )}
    </div>
  );
}
