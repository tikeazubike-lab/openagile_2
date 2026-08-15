import { useTutors } from "@/hooks/useTutors";
import { useUpdateTutor } from "@/hooks/useTutors";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Star, CheckCircle, XCircle } from "lucide-react";
import { getInitials, formatCurrency } from "@/lib/utils";

export function OwnerTutors() {
  const { data: tutors, isLoading } = useTutors();
  const updateTutor = useUpdateTutor();

  const handleToggleActive = (name: string, currentActive: boolean) => {
    updateTutor.mutate({ name, data: { is_active: currentActive ? 0 : 1 } });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Manage Tutors</h1>
        <Badge variant="secondary">{tutors?.length ?? 0} total</Badge>
      </div>

      {isLoading && (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-16 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      )}

      {tutors && (
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Tutor</TableHead>
                  <TableHead>Subjects</TableHead>
                  <TableHead>Rate</TableHead>
                  <TableHead>Rating</TableHead>
                  <TableHead>Sessions</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {tutors.map((tutor) => (
                  <TableRow key={tutor.name}>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <Avatar className="h-8 w-8">
                          <AvatarFallback className="bg-primary-100 text-primary-700 text-xs">
                            {getInitials(tutor.full_name)}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-medium text-sm">{tutor.full_name}</p>
                          <p className="text-xs text-muted-foreground">{tutor.email}</p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {tutor.subjects?.split(",").slice(0, 2).map((s) => (
                          <Badge key={s.trim()} variant="secondary" className="text-xs">
                            {s.trim()}
                          </Badge>
                        ))}
                      </div>
                    </TableCell>
                    <TableCell className="font-medium">{formatCurrency(tutor.hourly_rate)}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400" />
                        <span className="text-sm">{tutor.rating?.toFixed(1) || "—"}</span>
                      </div>
                    </TableCell>
                    <TableCell>{tutor.total_sessions}</TableCell>
                    <TableCell>
                      <Badge variant={tutor.is_active ? "success" : "destructive"}>
                        {tutor.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleToggleActive(tutor.name, tutor.is_active)}
                      >
                        {tutor.is_active ? (
                          <XCircle className="h-4 w-4 text-destructive" />
                        ) : (
                          <CheckCircle className="h-4 w-4 text-success" />
                        )}
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
