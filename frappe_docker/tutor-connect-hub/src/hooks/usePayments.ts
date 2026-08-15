import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { frappeApi } from "@/lib/frappe-api";
import type { Payment, DashboardStats, RevenueDataPoint } from "@/types";

const DOCTYPE = "Tutor Payment";

export function usePayments(filters?: {
  status?: string;
  tutor?: string;
  student?: string;
  limit?: number;
}) {
  return useQuery({
    queryKey: ["payments", filters],
    queryFn: () => {
      const frappeFilters: unknown[] = [];
      if (filters?.status) {
        frappeFilters.push(["status", "=", filters.status]);
      }
      if (filters?.tutor) {
        frappeFilters.push(["tutor", "=", filters.tutor]);
      }
      if (filters?.student) {
        frappeFilters.push(["student", "=", filters.student]);
      }
      return frappeApi.getList<Payment>(DOCTYPE, {
        filters: frappeFilters,
        fields: [
          "name",
          "session",
          "student",
          "student_name",
          "tutor",
          "tutor_name",
          "amount",
          "platform_fee",
          "tutor_payout",
          "status",
          "payment_date",
          "payment_method",
          "transaction_reference",
        ],
        order_by: "creation desc",
        limit: filters?.limit ?? 50,
      });
    },
  });
}

export function useDashboardStats() {
  return useQuery({
    queryKey: ["dashboardStats"],
    queryFn: () =>
      frappeApi.call<DashboardStats>(
        "tutor_hub.tutor_hub.api.get_dashboard_stats"
      ),
    refetchInterval: 60_000,
  });
}

export function useRevenueData(months = 6) {
  return useQuery({
    queryKey: ["revenueData", months],
    queryFn: () =>
      frappeApi.call<RevenueDataPoint[]>(
        "tutor_hub.tutor_hub.api.get_revenue_data",
        { months }
      ),
  });
}

export function useProcessPayout() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (paymentName: string) =>
      frappeApi.call("tutor_hub.tutor_hub.api.process_payout", {
        payment_id: paymentName,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["payments"] });
      queryClient.invalidateQueries({ queryKey: ["dashboardStats"] });
    },
  });
}
