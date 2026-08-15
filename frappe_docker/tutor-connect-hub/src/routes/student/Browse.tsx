import { TutorList } from "@/components/tutor/TutorList";

export function StudentBrowse() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Find a Tutor</h1>
        <p className="text-muted-foreground">Browse qualified tutors and book your next session</p>
      </div>
      <TutorList />
    </div>
  );
}
