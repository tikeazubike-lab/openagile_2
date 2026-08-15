import { usePayments } from "@/hooks/usePayments";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { formatCurrency, formatDate } from "@/lib/utils";

const statusVariant: Record<string, "default" | "success" | "warning" | "destructive"> = {
  Pending: "warning",
  Paid: "success",
  Failed: "destructive",
  Refunded: "destructive",
};

export function StudentPayments() {
  const { data: payments, isLoading } = usePayments();

  const totalPaid = payments?.filter((p) => p.status === "Paid").reduce((s, p) => s + p.amount, 0) ?? 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Payment History</h1>
        <div className="text-right">
          <p className="text-sm text-muted-foreground">Total Spent</p>
          <p className="text-xl font-bold text-primary-600">{formatCurrency(totalPaid)}</p>
        </div>
      </div>

      {isLoading && (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-12 rounded bg-muted animate-pulse" />
          ))}
        </div>
      )}

      {payments && (
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Session</TableHead>
                  <TableHead>Tutor</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Method</TableHead>
                  <TableHead>Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {payments.map((p) => (
                  <TableRow key={p.name}>
                    <TableCell className="font-mono text-xs">{p.session}</TableCell>
                    <TableCell>{p.tutor_name}</TableCell>
                    <TableCell className="font-medium">{formatCurrency(p.amount)}</TableCell>
                    <TableCell>
                      <Badge variant={statusVariant[p.status] || "secondary"}>{p.status}</Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {p.payment_method || "—"}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {p.payment_date ? formatDate(p.payment_date) : formatDate(p.creation)}
                    </TableCell>
                  </TableRow>
                ))}
                {payments.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} className="py-8 text-center text-muted-foreground">
                      No payment records yet.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
