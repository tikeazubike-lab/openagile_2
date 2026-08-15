import { BookingForm } from "@/components/session/BookingForm";

export function StudentBook() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Book a Session</h1>
        <p className="text-muted-foreground">Choose your subject, date, and time</p>
      </div>
      <BookingForm />
    </div>
  );
}
