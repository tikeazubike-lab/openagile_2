import { useAuth } from "@/hooks/useAuth";
import { useUpcomingSessions, useSessions } from "@/hooks/useSessions";
import { usePayments } from "@/hooks/usePayments";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SessionCard } from "@/components/session/SessionCard";
import { formatCurrency } from "@/lib/utils";
import { BookOpen, Clock, DollarSign, Search } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";

export function StudentDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { data: upcoming } = useUpcomingSessions();
  const { data: sessions } = useSessions({ limit: 10 });
  const { data: payments } = usePayments({ limit: 5 });

  const totalSpent = payments?.filter((p) => p.status === "Paid").reduce((s, p) => s + p.amount, 0) ?? 0;
  const completedSessions = sessions?.filter((s) => s.status === "Completed").length ?? 0;

  const statCards = [
    {
      title: "Total Spent",
      value: formatCurrency(totalSpent),
      icon: DollarSign,
      color: "text-emerald-600 bg-emerald-50",
    },
    {
      title: "Upcoming Sessions",
      value: upcoming?.length ?? 0,
      icon: Clock,
      color: "text-blue-600 bg-blue-50",
    },
    {
      title: "Completed Sessions",
      value: completedSessions,
      icon: BookOpen,
      color: "text-purple-600 bg-purple-50",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Welcome, {user?.full_name?.split(" ")[0] || "Student"}</h1>
          <p className="text-muted-foreground">Here&apos;s your learning overview</p>
        </div>
        <Button onClick={() => navigate("/student/browse")}>
          <Search className="mr-1.5 h-4 w-4" />
          Find Tutors
        </Button>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        {statCards.map((card) => (
          <Card key={card.title}>
            <CardContent className="p-5 flex items-center gap-4">
              <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${card.color}`}>
                <card.icon className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">{card.title}</p>
                <p className="text-xl font-bold">{card.value}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Upcoming Sessions</CardTitle>
          </CardHeader>
          <CardContent>
            {upcoming && upcoming.length > 0 ? (
              <div className="space-y-3">
                {upcoming.slice(0, 3).map((session) => (
                  <SessionCard key={session.name} session={session} role="student" />
                ))}
              </div>
            ) : (
              <div className="py-8 text-center">
                <Clock className="mx-auto h-8 w-8 text-muted-foreground/40 mb-2" />
                <p className="text-muted-foreground">No upcoming sessions</p>
                <Button variant="link" className="mt-2" onClick={() => navigate("/student/browse")}>
                  Find a tutor
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Sessions</CardTitle>
          </CardHeader>
          <CardContent>
            {sessions && sessions.length > 0 ? (
              <div className="space-y-3">
                {sessions.slice(0, 3).map((session) => (
                  <SessionCard key={session.name} session={session} role="student" />
                ))}
              </div>
            ) : (
              <div className="py-8 text-center text-muted-foreground">
                No sessions yet. Book your first session!
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
