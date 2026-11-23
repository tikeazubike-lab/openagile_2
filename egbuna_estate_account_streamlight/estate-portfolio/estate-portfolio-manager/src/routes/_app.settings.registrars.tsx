import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuthStore } from "@/store/authStore";
import { fetchApiEnvelope } from "@/api/queries";
import { Mail, Send, Loader2, CheckCircle, XCircle } from "lucide-react";

export const Route = createFileRoute("/_app/settings/registrars")({
  component: RegistrarsSettingsPage,
});

function RegistrarsSettingsPage() {
  const isAdmin = useAuthStore((s) => s.isAdmin)();

  if (!isAdmin) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center text-muted-foreground">
        Access denied — admin only.
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col overflow-hidden bg-background">
      <div className="border-b p-4">
        <h1 className="text-xl font-semibold">Registrar Settings</h1>
        <p className="text-sm text-muted-foreground">
          Email reminders for registrar document deadlines.
        </p>
      </div>
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <TestSendCard />
        <ReminderLogCard />
      </div>
    </div>
  );
}

export function TestSendCard() {
  const queryClient = useQueryClient();
  const [result, setResult] = useState<{ status: string; detail?: string } | null>(null);

  const testSend = useMutation({
    mutationFn: async () => {
      // fetchApiEnvelope throws on non-OK HTTP (FastAPI `detail`) or an envelope
      // error field, and returns the { data, meta, error } envelope — unwrap data.
      return fetchApiEnvelope<{
        status?: string;
        recipient?: string;
        detail?: string;
      }>("/api/v1/admin/reminders/test-send", { method: "POST" });
    },
    onSuccess: (env) => {
      const payload = env.data ?? {};
      setResult({
        status: payload.status ?? "sent",
        detail: payload.detail ?? `Sent to ${payload.recipient ?? "unknown recipient"}`,
      });
    },
    onError: (err: Error) => {
      setResult({ status: "failed", detail: err.message });
    },
  });

  return (
    <div className="rounded-lg border border-border/30 bg-card p-4">
      <h3 className="text-sm font-medium mb-3 flex items-center gap-2">
        <Mail className="h-4 w-4" />
        Test Email
      </h3>
      <p className="text-xs text-muted-foreground mb-3">
        Send a test email to verify SMTP configuration is working.
      </p>
      <Button
        onClick={() => testSend.mutate()}
        disabled={testSend.isPending}
        size="sm"
      >
        {testSend.isPending ? (
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        ) : (
          <Send className="mr-2 h-4 w-4" />
        )}
        Send Test Email
      </Button>
      {result && (
        <div className={cn(
          "mt-3 text-sm flex items-center gap-2",
          result.status === "sent" ? "text-green-500" : "text-red-500"
        )}>
          {result.status === "sent" ? (
            <CheckCircle className="h-4 w-4" />
          ) : (
            <XCircle className="h-4 w-4" />
          )}
          {result.detail}
        </div>
      )}
    </div>
  );
}

export function ReminderLogCard() {
  const [page, setPage] = useState(1);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["reminder-log", page],
    queryFn: async () => {
      // fetchApiEnvelope throws on !res.ok and on an envelope error field, so
      // 4xx/5xx surface as isError below instead of the empty state.
      const env = await fetchApiEnvelope<any>(
        `/api/v1/admin/reminders/log?page=${page}&page_size=10`,
      );
      // As built in registrars.py, rows + pagination are nested inside the
      // envelope's data field: { data: { data: rows, meta: pagination }, ... }.
      const payload = env.data;
      const rows = Array.isArray(payload) ? payload : (payload?.data ?? []);
      const meta =
        payload && !Array.isArray(payload) && payload.meta
          ? payload.meta
          : (env.meta ?? {});
      return { rows, meta };
    },
  });

  const logs = data?.rows ?? [];
  const meta = data?.meta ?? {};

  return (
    <div className="rounded-lg border border-border/30 bg-card p-4">
      <h3 className="text-sm font-medium mb-3 flex items-center gap-2">
        <Mail className="h-4 w-4" />
        Reminder Log
      </h3>
      {isLoading ? (
        <div className="text-sm text-muted-foreground py-4">Loading...</div>
      ) : isError ? (
        <div className="text-sm text-red-500 py-4">
          Failed to load reminder log:{" "}
          {error instanceof Error ? error.message : "Unknown error"}
        </div>
      ) : logs.length === 0 ? (
        <div className="text-sm text-muted-foreground py-4">No reminders sent yet.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-muted-foreground">
                <th className="pb-2 font-medium">Date</th>
                <th className="pb-2 font-medium">Type</th>
                <th className="pb-2 font-medium">Requirement</th>
                <th className="pb-2 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log: any) => (
                <tr key={log.id} className="border-b last:border-0">
                  <td className="py-2 text-muted-foreground">
                    {log.sent_at ? new Date(log.sent_at).toLocaleDateString() : "-"}
                  </td>
                  <td className="py-2">
                    <Badge variant={log.reminder_type === "overdue" ? "destructive" : "secondary"}>
                      {log.reminder_type}
                    </Badge>
                  </td>
                  <td className="py-2">
                    <div className="font-medium">{log.requirement_title}</div>
                  </td>
                  <td className="py-2">
                    <Badge variant={log.delivery_status === "sent" ? "default" : "destructive"}>
                      {log.delivery_status}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {meta.total_pages > 1 && (
            <div className="flex items-center justify-between mt-4 pt-4 border-t">
              <span className="text-sm text-muted-foreground">
                Page {meta.page} of {meta.total_pages} ({meta.total} total)
              </span>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => p - 1)}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page >= meta.total_pages}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Reuse existing UI components
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
