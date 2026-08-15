import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Calendar, Clock, Video, Star, User } from "lucide-react";
import { formatDate, formatTime, formatCurrency } from "@/lib/utils";
import type { Session } from "@/types";

interface SessionCardProps {
  session: Session;
  role: "student" | "tutor" | "owner";
  onUpdateStatus?: (name: string, status: string) => void;
}

const statusVariant: Record<string, "default" | "success" | "warning" | "destructive" | "secondary"> = {
  Pending: "warning",
  Confirmed: "default",
  "In Progress": "default",
  Completed: "success",
  Cancelled: "destructive",
  "No Show": "destructive",
};

export function SessionCard({ session, role, onUpdateStatus }: SessionCardProps) {
  const otherPerson = role === "student" ? session.tutor_name : session.student_name;
  const otherLabel = role === "student" ? "Tutor" : "Student";

  return (
    <Card className="overflow-hidden transition-all hover:shadow-md">
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-semibold text-foreground truncate">{session.subject}</h3>
              <Badge variant={statusVariant[session.status] || "secondary"}>{session.status}</Badge>
            </div>
            <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
              <User className="h-3.5 w-3.5" />
              <span>{otherLabel}: {otherPerson}</span>
            </div>
          </div>
          <div className="text-right shrink-0">
            <p className="text-sm font-bold text-primary-600">{formatCurrency(session.total_amount)}</p>
            {session.rating && (
              <div className="flex items-center gap-0.5 justify-end text-amber-500">
                <Star className="h-3.5 w-3.5 fill-current" />
                <span className="text-xs font-medium">{session.rating}</span>
              </div>
            )}
          </div>
        </div>

        <div className="mt-3 flex flex-wrap gap-3 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <Calendar className="h-4 w-4" />
            <span>{formatDate(session.session_date)}</span>
          </div>
          <div className="flex items-center gap-1">
            <Clock className="h-4 w-4" />
            <span>{formatTime(session.start_time)} - {formatTime(session.end_time)}</span>
          </div>
        </div>

        {session.notes && (
          <p className="mt-3 text-sm text-muted-foreground line-clamp-2">{session.notes}</p>
        )}

        {session.feedback && (
          <div className="mt-3 rounded-lg bg-gray-50 p-3">
            <p className="text-xs font-medium text-muted-foreground mb-1">Feedback</p>
            <p className="text-sm">{session.feedback}</p>
          </div>
        )}

        <div className="mt-4 flex items-center gap-2 border-t border-border pt-3">
          {session.meeting_link && (session.status === "Confirmed" || session.status === "In Progress") && (
            <Button size="sm" asChild>
              <a href={session.meeting_link} target="_blank" rel="noopener noreferrer">
                <Video className="mr-1.5 h-3.5 w-3.5" />
                Join Meeting
              </a>
            </Button>
          )}
          {session.status === "Pending" && onUpdateStatus && (
            <>
              <Button size="sm" variant="outline" onClick={() => onUpdateStatus(session.name, "Cancelled")}>
                Cancel
              </Button>
              {role === "tutor" && (
                <Button size="sm" onClick={() => onUpdateStatus(session.name, "Confirmed")}>
                  Confirm
                </Button>
              )}
            </>
          )}
          {session.status === "Confirmed" && onUpdateStatus && role === "tutor" && (
            <Button size="sm" onClick={() => onUpdateStatus(session.name, "Completed")}>
              Mark Complete
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
