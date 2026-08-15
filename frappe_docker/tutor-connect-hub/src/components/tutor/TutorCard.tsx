import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Star, Clock, BookOpen } from "lucide-react";
import { getInitials, formatCurrency } from "@/lib/utils";
import type { Tutor } from "@/types";

interface TutorCardProps {
  tutor: Tutor;
}

export function TutorCard({ tutor }: TutorCardProps) {
  const navigate = useNavigate();
  const subjects = tutor.subjects
    ? tutor.subjects.split(",").map((s) => s.trim()).filter(Boolean)
    : [];

  return (
    <Card className="group overflow-hidden transition-all hover:shadow-lg hover:border-primary-200">
      <CardContent className="p-6">
        <div className="flex items-start gap-4">
          <Avatar className="h-14 w-14 shrink-0">
            <AvatarFallback className="bg-primary-100 text-primary-700 text-lg font-semibold">
              {getInitials(tutor.full_name)}
            </AvatarFallback>
          </Avatar>
          <div className="min-w-0 flex-1">
            <h3 className="font-semibold text-foreground truncate">{tutor.full_name}</h3>
            <p className="text-sm text-muted-foreground mt-0.5 line-clamp-2">
              {tutor.bio || "Experienced tutor ready to help you succeed."}
            </p>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap gap-1.5">
          {subjects.slice(0, 3).map((subject) => (
            <Badge key={subject} variant="secondary" className="text-xs">
              {subject}
            </Badge>
          ))}
          {subjects.length > 3 && (
            <Badge variant="secondary" className="text-xs">
              +{subjects.length - 3} more
            </Badge>
          )}
        </div>

        <div className="mt-4 flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <Star className="h-4 w-4 fill-amber-400 text-amber-400" />
            <span className="font-medium text-foreground">{tutor.rating?.toFixed(1) || "New"}</span>
          </div>
          <div className="flex items-center gap-1">
            <BookOpen className="h-4 w-4" />
            <span>{tutor.total_sessions || 0} sessions</span>
          </div>
          <div className="flex items-center gap-1">
            <Clock className="h-4 w-4" />
            <span>{tutor.experience_years || 0}yr exp</span>
          </div>
        </div>

        <div className="mt-5 flex items-center justify-between border-t border-border pt-4">
          <div>
            <p className="text-xs text-muted-foreground">Per hour</p>
            <p className="text-lg font-bold text-primary-600">
              {formatCurrency(tutor.hourly_rate)}
            </p>
          </div>
          <Button size="sm" onClick={() => navigate(`/student/book?tutor=${tutor.name}`)}>
            Book Session
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
