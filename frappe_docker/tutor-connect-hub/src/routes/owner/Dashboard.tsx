import { useDashboardStats, useRevenueData } from "@/hooks/usePayments";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCurrency } from "@/lib/utils";
import { Users, BookOpen, TrendingUp, Star } from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";

export function OwnerDashboard() {
  const { data: stats, isLoading } = useDashboardStats();
  const { data: revenueData } = useRevenueData(6);

  const statCards = [
    {
      title: "Total Revenue",
      value: stats ? formatCurrency(stats.total_revenue) : "—",
      icon: TrendingUp,
      color: "text-emerald-600 bg-emerald-50",
    },
    {
      title: "Active Tutors",
      value: stats?.active_tutors ?? "—",
      icon: Users,
      color: "text-blue-600 bg-blue-50",
    },
    {
      title: "Total Sessions",
      value: stats?.total_sessions ?? "—",
      icon: BookOpen,
      color: "text-purple-600 bg-purple-50",
    },
    {
      title: "Completion Rate",
      value: stats ? `${stats.completion_rate.toFixed(0)}%` : "—",
      icon: Star,
      color: "text-amber-600 bg-amber-50",
    },
  ];

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Owner Dashboard</h1>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-28 rounded-xl bg-muted animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Owner Dashboard</h1>

      {/* Stat cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((card) => (
          <Card key={card.title}>
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">{card.title}</p>
                  <p className="mt-1 text-2xl font-bold">{card.value}</p>
                </div>
                <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${card.color}`}>
                  <card.icon className="h-5 w-5" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Revenue Over Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={revenueData || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                  <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="#94A3B8" />
                  <YAxis tick={{ fontSize: 12 }} stroke="#94A3B8" />
                  <Tooltip
                    contentStyle={{
                      borderRadius: "8px",
                      border: "1px solid #E2E8F0",
                      boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)",
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="revenue"
                    stroke="#4F46E5"
                    fill="#EEF2FF"
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Sessions Per Month</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={revenueData || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                  <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="#94A3B8" />
                  <YAxis tick={{ fontSize: 12 }} stroke="#94A3B8" />
                  <Tooltip
                    contentStyle={{
                      borderRadius: "8px",
                      border: "1px solid #E2E8F0",
                      boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)",
                    }}
                  />
                  <Bar dataKey="sessions" fill="#4F46E5" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
