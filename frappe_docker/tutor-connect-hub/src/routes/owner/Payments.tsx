import { usePayments, useProcessPayout } from "@/hooks/usePayments";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { formatCurrency, formatDate } from "@/lib/utils";

const statusVariant: Record<string, "default" | "success" | "warning" | "destructive"> = {
  Pending: "warning",
  Paid: "success",
  Failed: "destructive",
  Refunded: "destructive",
};

export function OwnerPayments() {
  const { data: payments, isLoading } = usePayments();
  const processPayout = useProcessPayout();

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Payments</h1>

      {isLoading && (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-16 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      )}

      {payments && (
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Student</TableHead>
                  <TableHead>Tutor</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Platform Fee</TableHead>
                  <TableHead>Tutor Payout</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {payments.map((p) => (
                  <TableRow key={p.name}>
                    <TableCell className="font-mono text-xs">{p.name}</TableCell>
                    <TableCell className="text-sm">{p.student_name}</TableCell>
                    <TableCell className="text-sm">{p.tutor_name}</TableCell>
                    <TableCell className="font-medium">{formatCurrency(p.amount)}</TableCell>
                    <TableCell className="text-muted-foreground">{formatCurrency(p.platform_fee)}</TableCell>
                    <TableCell className="font-medium text-emerald-600">{formatCurrency(p.tutor_payout)}</TableCell>
                    <TableCell>
                      <Badge variant={statusVariant[p.status] || "secondary"}>{p.status}</Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {p.payment_date ? formatDate(p.payment_date) : "—"}
                    </TableCell>
                    <TableCell className="text-right">
                      {p.status === "Pending" && (
                        <Button
                          size="sm"
                          onClick={() => processPayout.mutate(p.name)}
                          loading={processPayout.isPending}
                        >
                          Process
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
                {payments.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={9} className="py-8 text-center text-muted-foreground">
                      No payments found.
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
