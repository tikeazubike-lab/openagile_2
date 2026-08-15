import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { frappeApi } from "@/lib/frappe-api";
import type { Session } from "@/types";

const DOCTYPE = "Tutoring Session";

export function useSessions(filters?: {
  status?: string;
  tutor?: string;
  student?: string;
  limit?: number;
}) {
  return useQuery({
    queryKey: ["sessions", filters],
    queryFn: () => {
      const frappeFilters: Record<string, unknown>[] = [];
      if (filters?.status) {
        frappeFilters.push(["status", "=", filters.status]);
      }
      if (filters?.tutor) {
        frappeFilters.push(["tutor", "=", filters.tutor]);
      }
      if (filters?.student) {
        frappeFilters.push(["student", "=", filters.student]);
      }
      return frappeApi.getList<Session>(DOCTYPE, {
        filters: frappeFilters,
        fields: [
          "name",
          "student",
          "student_name",
          "tutor",
          "tutor_name",
          "subject",
          "session_date",
          "start_time",
          "end_time",
          "duration_hours",
          "status",
          "hourly_rate",
          "total_amount",
          "platform_fee",
          "notes",
          "meeting_link",
          "rating",
          "feedback",
        ],
        order_by: "session_date desc, start_time desc",
        limit: filters?.limit ?? 50,
      });
    },
  });
}

export function useSession(name: string | undefined) {
  return useQuery({
    queryKey: ["session", name],
    queryFn: () => frappeApi.getDoc<Session>(DOCTYPE, name!),
    enabled: !!name,
  });
}

export function useUpcomingSessions() {
  return useQuery({
    queryKey: ["sessions", "upcoming"],
    queryFn: () =>
      frappeApi.getList<Session>(DOCTYPE, {
        filters: [
          ["status", "in", ["Pending", "Confirmed"]],
          ["session_date", ">=", new Date().toISOString().split("T")[0]],
        ],
        order_by: "session_date asc, start_time asc",
        limit: 10,
      }),
  });
}

export function useBookSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      tutor: string;
      subject: string;
      session_date: string;
      start_time: string;
      end_time: string;
      notes?: string;
    }) =>
      frappeApi.call<{ session: Session }>(
        "tutor_hub.tutor_hub.api.book_session",
        data
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
    },
  });
}

export function useUpdateSessionStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      name,
      status,
      feedback,
      rating,
    }: {
      name: string;
      status: string;
      feedback?: string;
      rating?: number;
    }) =>
      frappeApi.call("tutor_hub.tutor_hub.api.update_session_status", {
        session_id: name,
        status,
        feedback,
        rating,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
    },
  });
}
