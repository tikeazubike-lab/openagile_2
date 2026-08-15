import { useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { useTutor } from "@/hooks/useTutors";
import { useBookSession } from "@/hooks/useSessions";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { CalendarDays, Clock, Star, BookOpen } from "lucide-react";
import { getInitials, formatCurrency } from "@/lib/utils";
import { SUBJECTS } from "@/lib/constants";

const TIME_SLOTS = [
  "08:00", "09:00", "10:00", "11:00", "12:00",
  "13:00", "14:00", "15:00", "16:00", "17:00", "18:00",
];

export function BookingForm() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const tutorName = searchParams.get("tutor") || "";

  const { data: tutor, isLoading: tutorLoading } = useTutor(tutorName || undefined);
  const bookSession = useBookSession();

  const [subject, setSubject] = useState("");
  const [sessionDate, setSessionDate] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [notes, setNotes] = useState("");

  const durationHours =
    startTime && endTime
      ? Math.max(
          0,
          (parseInt(endTime.split(":")[0]!) - parseInt(startTime.split(":")[0]!))
        )
      : 0;

  const totalAmount = tutor ? tutor.hourly_rate * Math.max(durationHours, 1) : 0;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tutorName || !subject || !sessionDate || !startTime || !endTime) return;

    try {
      await bookSession.mutateAsync({
        tutor: tutorName,
        subject,
        session_date: sessionDate,
        start_time: startTime + ":00",
        end_time: endTime + ":00",
        notes: notes || undefined,
      });
      navigate("/student/sessions");
    } catch {
      // error handled by mutation
    }
  };

  if (tutorLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-500 border-t-transparent" />
      </div>
    );
  }

  if (!tutor) {
    return (
      <div className="text-center py-20">
        <p className="text-muted-foreground">Please select a tutor first.</p>
        <Button className="mt-4" onClick={() => navigate("/student/browse")}>
          Browse Tutors
        </Button>
      </div>
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      {/* Tutor info sidebar */}
      <div className="lg:col-span-1">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Tutor Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-3">
              <Avatar className="h-12 w-12">
                <AvatarFallback className="bg-primary-100 text-primary-700 text-lg">
                  {getInitials(tutor.full_name)}
                </AvatarFallback>
              </Avatar>
              <div>
                <p className="font-semibold">{tutor.full_name}</p>
                <div className="flex items-center gap-1 text-sm text-muted-foreground">
                  <Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400" />
                  <span>{tutor.rating?.toFixed(1) || "New"}</span>
                  <span className="mx-1">·</span>
                  <BookOpen className="h-3.5 w-3.5" />
                  <span>{tutor.total_sessions || 0} sessions</span>
                </div>
              </div>
            </div>
            {tutor.bio && (
              <p className="text-sm text-muted-foreground">{tutor.bio}</p>
            )}
            <div className="flex flex-wrap gap-1.5">
              {tutor.subjects?.split(",").map((s) => (
                <Badge key={s.trim()} variant="secondary" className="text-xs">
                  {s.trim()}
                </Badge>
              ))}
            </div>
            <div className="rounded-lg bg-primary-50 p-3 text-center">
              <p className="text-xs text-primary-600">Hourly Rate</p>
              <p className="text-xl font-bold text-primary-700">
                {formatCurrency(tutor.hourly_rate)}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Booking form */}
      <div className="lg:col-span-2">
        <Card>
          <CardHeader>
            <CardTitle>Book a Session</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="space-y-2">
                <Label htmlFor="subject">Subject</Label>
                <Select value={subject} onValueChange={setSubject} required>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a subject" />
                  </SelectTrigger>
                  <SelectContent>
                    {SUBJECTS.map((s) => (
                      <SelectItem key={s} value={s}>
                        {s}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="date">Session Date</Label>
                <div className="relative">
                  <CalendarDays className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="date"
                    type="date"
                    className="pl-9"
                    value={sessionDate}
                    onChange={(e) => setSessionDate(e.target.value)}
                    min={new Date().toISOString().split("T")[0]}
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Start Time</Label>
                  <Select value={startTime} onValueChange={setStartTime} required>
                    <SelectTrigger>
                      <SelectValue placeholder="Select time" />
                    </SelectTrigger>
                    <SelectContent>
                      {TIME_SLOTS.slice(0, -1).map((t) => (
                        <SelectItem key={t} value={t}>
                          {t}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>End Time</Label>
                  <Select value={endTime} onValueChange={setEndTime} required>
                    <SelectTrigger>
                      <SelectValue placeholder="Select time" />
                    </SelectTrigger>
                    <SelectContent>
                      {TIME_SLOTS.filter((t) => !startTime || t > startTime).map((t) => (
                        <SelectItem key={t} value={t}>
                          {t}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="notes">Notes (optional)</Label>
                <textarea
                  id="notes"
                  className="flex min-h-[80px] w-full rounded-lg border border-border bg-white px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
                  placeholder="Any specific topics or questions you'd like to cover..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                />
              </div>

              {/* Summary */}
              {durationHours > 0 && (
                <div className="rounded-lg border border-border bg-gray-50 p-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Duration</span>
                    <span className="font-medium">{durationHours} hour(s)</span>
                  </div>
                  <div className="flex items-center justify-between text-sm mt-1">
                    <span className="text-muted-foreground">Rate</span>
                    <span className="font-medium">{formatCurrency(tutor.hourly_rate)}/hr</span>
                  </div>
                  <div className="mt-2 border-t border-border pt-2 flex items-center justify-between">
                    <span className="font-semibold">Total</span>
                    <span className="text-lg font-bold text-primary-600">
                      {formatCurrency(totalAmount)}
                    </span>
                  </div>
                </div>
              )}

              <Button
                type="submit"
                className="w-full"
                size="lg"
                loading={bookSession.isPending}
                disabled={!subject || !sessionDate || !startTime || !endTime}
              >
                <Clock className="mr-2 h-4 w-4" />
                Book Session
              </Button>

              {bookSession.isError && (
                <p className="text-sm text-destructive text-center">
                  {bookSession.error?.message || "Failed to book session. Please try again."}
                </p>
              )}
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
