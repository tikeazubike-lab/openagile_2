import { useMyTutorProfile } from "@/hooks/useTutors";
import { useSessions } from "@/hooks/useSessions";
import { usePayments } from "@/hooks/usePayments";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { SessionCard } from "@/components/session/SessionCard";
import { formatCurrency } from "@/lib/utils";
import { BookOpen, Clock, DollarSign, Star } from "lucide-react";

export function TutorDashboard() {
  const { data: profile } = useMyTutorProfile();
  const { data: sessions } = useSessions({ tutor: profile?.name, limit: 5 });
  const { data: payments } = usePayments({ tutor: profile?.name, limit: 5 });

  const totalEarnings =
    payments?.filter((p) => p.status === "Paid").reduce((sum, p) => sum + p.tutor_payout, 0) ?? 0;
  const upcomingSessions = sessions?.filter(
    (s) => s.status === "Pending" || s.status === "Confirmed"
  );

  const statCards = [
    {
      title: "Total Earnings",
      value: formatCurrency(totalEarnings),
      icon: DollarSign,
      color: "text-emerald-600 bg-emerald-50",
    },
    {
      title: "Upcoming Sessions",
      value: upcomingSessions?.length ?? 0,
      icon: Clock,
      color: "text-blue-600 bg-blue-50",
    },
    {
      title: "Total Sessions",
      value: profile?.total_sessions ?? 0,
      icon: BookOpen,
      color: "text-purple-600 bg-purple-50",
    },
    {
      title: "Rating",
      value: profile?.rating?.toFixed(1) ?? "New",
      icon: Star,
      color: "text-amber-600 bg-amber-50",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Tutor Dashboard</h1>
        {profile && (
          <Badge variant={profile.is_active ? "success" : "destructive"}>
            {profile.is_active ? "Active" : "Inactive"}
          </Badge>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((card) => (
          <Card key={card.title}>
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">{card.title}</p>
                  <p className="mt-1 text-2xl font-bold">{card.value}</p>
                </div>
                <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${card.color}`}>
                  <card.icon className="h-5 w-5" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Upcoming sessions */}
      <Card>
        <CardHeader>
          <CardTitle>Upcoming Sessions</CardTitle>
        </CardHeader>
        <CardContent>
          {upcomingSessions && upcomingSessions.length > 0 ? (
            <div className="space-y-3">
              {upcomingSessions.map((session) => (
                <SessionCard key={session.name} session={session} role="tutor" />
              ))}
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-8">No upcoming sessions.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
