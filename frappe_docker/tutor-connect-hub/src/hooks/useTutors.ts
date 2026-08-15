import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { frappeApi } from "@/lib/frappe-api";
import type { Tutor } from "@/types";

const DOCTYPE = "Tutor";

export function useTutors(filters?: { subject?: string; active?: boolean }) {
  return useQuery({
    queryKey: ["tutors", filters],
    queryFn: () => {
      const frappeFilters: unknown[] = [];
      if (filters?.subject) {
        frappeFilters.push(["subjects", "like", `%${filters.subject}%`]);
      }
      if (filters?.active !== undefined) {
        frappeFilters.push(["is_active", "=", filters.active ? 1 : 0]);
      }
      return frappeApi.getList<Tutor>(DOCTYPE, {
        filters: frappeFilters,
        fields: [
          "name",
          "full_name",
          "email",
          "phone",
          "bio",
          "subjects",
          "hourly_rate",
          "experience_years",
          "qualifications",
          "rating",
          "total_sessions",
          "is_active",
          "profile_image",
        ],
        order_by: "rating desc",
        limit: 50,
      });
    },
  });
}

export function useTutor(name: string | undefined) {
  return useQuery({
    queryKey: ["tutor", name],
    queryFn: () => frappeApi.getDoc<Tutor>(DOCTYPE, name!),
    enabled: !!name,
  });
}

export function useMyTutorProfile() {
  return useQuery({
    queryKey: ["myTutorProfile"],
    queryFn: async () => {
      const user = await frappeApi.getSessionUser();
      if (!user.message) throw new Error("Not authenticated");
      const tutors = await frappeApi.getList<Tutor>(DOCTYPE, {
        filters: [["owner", "=", user.message.user]],
        limit: 1,
      });
      return tutors[0] ?? null;
    },
  });
}

export function useUpdateTutor() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      name,
      data,
    }: {
      name: string;
      data: Record<string, unknown>;
    }) => frappeApi.updateDoc<Tutor>(DOCTYPE, name, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tutors"] });
      queryClient.invalidateQueries({ queryKey: ["myTutorProfile"] });
    },
  });
}
