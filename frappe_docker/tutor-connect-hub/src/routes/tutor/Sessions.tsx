import { useState } from "react";
import { useSessions, useUpdateSessionStatus } from "@/hooks/useSessions";
import { useMyTutorProfile } from "@/hooks/useTutors";
import { SessionCard } from "@/components/session/SessionCard";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export function TutorSessions() {
  const { data: profile } = useMyTutorProfile();
  const [statusFilter, setStatusFilter] = useState<string>("");
  const { data: sessions, isLoading } = useSessions({
    tutor: profile?.name,
    status: statusFilter || undefined,
  });
  const updateStatus = useUpdateSessionStatus();

  const handleUpdateStatus = (name: string, status: string) => {
    updateStatus.mutate({ name, status });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">My Sessions</h1>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="All Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Status</SelectItem>
            <SelectItem value="Pending">Pending</SelectItem>
            <SelectItem value="Confirmed">Confirmed</SelectItem>
            <SelectItem value="Completed">Completed</SelectItem>
            <SelectItem value="Cancelled">Cancelled</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {isLoading && (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-32 rounded-xl bg-muted animate-pulse" />
          ))}
        </div>
      )}

      {sessions && sessions.length > 0 && (
        <div className="space-y-3">
          {sessions.map((session) => (
            <SessionCard
              key={session.name}
              session={session}
              role="tutor"
              onUpdateStatus={handleUpdateStatus}
            />
          ))}
        </div>
      )}

      {sessions && sessions.length === 0 && (
        <div className="rounded-lg border border-border bg-gray-50 p-12 text-center">
          <p className="text-muted-foreground">No sessions found.</p>
        </div>
      )}
    </div>
  );
}
