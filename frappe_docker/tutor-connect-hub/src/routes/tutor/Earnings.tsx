import { usePayments } from "@/hooks/usePayments";
import { useMyTutorProfile } from "@/hooks/useTutors";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { formatCurrency, formatDate } from "@/lib/utils";
import { DollarSign, TrendingUp, Clock } from "lucide-react";

const statusVariant: Record<string, "default" | "success" | "warning" | "destructive"> = {
  Pending: "warning",
  Paid: "success",
  Failed: "destructive",
  Refunded: "destructive",
};

export function TutorEarnings() {
  const { data: profile } = useMyTutorProfile();
  const { data: payments, isLoading } = usePayments({ tutor: profile?.name });

  const totalPaid = payments?.filter((p) => p.status === "Paid").reduce((s, p) => s + p.tutor_payout, 0) ?? 0;
  const totalPending = payments?.filter((p) => p.status === "Pending").reduce((s, p) => s + p.tutor_payout, 0) ?? 0;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Earnings</h1>

      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="p-5 flex items-center gap-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600">
              <DollarSign className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Paid</p>
              <p className="text-xl font-bold">{formatCurrency(totalPaid)}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5 flex items-center gap-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-50 text-amber-600">
              <Clock className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Pending</p>
              <p className="text-xl font-bold">{formatCurrency(totalPending)}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5 flex items-center gap-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
              <TrendingUp className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Sessions</p>
              <p className="text-xl font-bold">{profile?.total_sessions ?? 0}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Payment History</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading && (
            <div className="p-6 space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="h-12 rounded bg-muted animate-pulse" />
              ))}
            </div>
          )}
          {payments && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Session</TableHead>
                  <TableHead>Student</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Platform Fee</TableHead>
                  <TableHead>Payout</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {payments.map((p) => (
                  <TableRow key={p.name}>
                    <TableCell className="font-mono text-xs">{p.session}</TableCell>
                    <TableCell>{p.student_name}</TableCell>
                    <TableCell>{formatCurrency(p.amount)}</TableCell>
                    <TableCell className="text-muted-foreground">{formatCurrency(p.platform_fee)}</TableCell>
                    <TableCell className="font-medium">{formatCurrency(p.tutor_payout)}</TableCell>
                    <TableCell>
                      <Badge variant={statusVariant[p.status] || "secondary"}>{p.status}</Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {p.payment_date ? formatDate(p.payment_date) : "—"}
                    </TableCell>
                  </TableRow>
                ))}
                {payments.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={7} className="py-8 text-center text-muted-foreground">
                      No payment records yet.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
