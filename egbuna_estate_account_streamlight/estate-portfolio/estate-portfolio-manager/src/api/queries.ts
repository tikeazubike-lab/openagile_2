// EPM Phase 2 — TanStack Query hooks for all /api/v1/* endpoints.
// Phase 2A: queryFns call real API. Falls back gracefully if backend is not running.
// Replace the delay(MOCK_*) pattern with real fetch calls as each endpoint is live.

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import type { DashboardData, Holding, ApiResponse, Company } from "@/types";
import { MOCK_DASHBOARD, MOCK_HOLDINGS } from "./mock";

// ─── Helpers ───────────────────────────────────────────────────────────────────

/** Human-readable message from FastAPI HTTPException / validation error bodies. */
function formatApiErrorBody(status: number, body: unknown): string {
  if (body && typeof body === "object" && body !== null && "detail" in body) {
    const detail = (body as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail
        .map((item) => {
          if (item && typeof item === "object" && item !== null && "msg" in item) {
            return String((item as { msg: string }).msg);
          }
          return JSON.stringify(item);
        })
        .join("; ");
    }
    if (detail !== undefined && detail !== null) return String(detail);
  }
  if (typeof body === "string") return body;
  return `Request failed (${status})`;
}

/**
 * POST etc. — returns full API envelope; throws on non-OK HTTP or envelope error field.
 */
async function fetchApiEnvelope<T>(path: string, init?: RequestInit): Promise<ApiResponse<T>> {
  const res = await fetch(path, { credentials: "include", ...init });
  let body: unknown = {};
  try {
    body = await res.json();
  } catch {
    /* non-JSON body */
  }
  if (!res.ok) {
    throw new Error(formatApiErrorBody(res.status, body));
  }
  const json = body as ApiResponse<T>;
  if (json.error) throw new Error(json.error);
  return json;
}

/** Fetch wrapper that unwraps the { data, meta, error } envelope. */
async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, { credentials: "include", ...init });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status} ${text}`);
  }
  const json: ApiResponse<T> = await res.json();
  if (json.error) throw new Error(json.error);
  return json.data;
}

/** Simulate realistic loading lag for mock data during development. */
const delay = <T>(data: T, ms = 400): Promise<T> =>
  new Promise((r) => setTimeout(() => r(data), ms));

// ─── Auth ──────────────────────────────────────────────────────────────────────

export interface LoginPayload {
  username: string;
  password: string;
}

export function useLogin() {
  return useMutation({
    mutationFn: (payload: LoginPayload) =>
      apiFetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }),
  });
}

export function useLogout() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => apiFetch("/api/v1/auth/logout", { method: "POST" }),
    onSuccess: () => qc.clear(),
  });
}

// ─── Dashboard ─────────────────────────────────────────────────────────────────

export function useDashboard() {
  return useQuery<DashboardData>({
    queryKey: ["dashboard"],
    queryFn: () => apiFetch<DashboardData>("/api/v1/dashboard"),
    refetchInterval: 60_000,
  });
}

export function useActionItems() {
  const { data: dashboard, isLoading } = useDashboard();

  if (isLoading || !dashboard) {
    return { data: { items: [], count: 0 }, isLoading: true };
  }

  const items = dashboard?.action_items ?? [];

  return {
    data: {
      items,
      count: items.length,
    },
    isLoading: false,
  };
}

// ─── Holdings ──────────────────────────────────────────────────────────────────

export function useHoldings() {
  return useQuery<Holding[]>({
    queryKey: ["holdings"],
    queryFn: () => apiFetch<Holding[]>("/api/v1/holdings"),
  });
}

export function useAddHolding() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: any) =>
      fetchApiEnvelope("/api/v1/holdings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["holdings"] });
      qc.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useUpdateHolding() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...payload }: { 
      id: number;
      num_shares?: number;
      avg_purchase_price?: string;
    }) =>
      fetchApiEnvelope(`/api/v1/holdings/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["holdings"] });
      qc.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useDeleteHolding() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) =>
      fetchApiEnvelope(`/api/v1/holdings/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["holdings"] });
      qc.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function usePublishHolding() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) =>
      fetchApiEnvelope(`/api/v1/holdings/${id}/publish`, { method: "POST" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["holdings"] });
      qc.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

// ─── NAV History ───────────────────────────────────────────────────────────────

export function useNavHistory() {
  return useQuery({
    queryKey: ["nav-history"],
    queryFn: () => apiFetch("/api/v1/nav-history"),
    enabled: false,
  });
}

// ─── Rebalancing ───────────────────────────────────────────────────────────────

export function useRebalancing() {
  return useQuery({
    queryKey: ["rebalancing"],
    queryFn: () => apiFetch("/api/v1/rebalancing"),
    enabled: false,
  });
}

// ─── Price Entry ──────────────────────────────────────────────────────────────

export function useCompanies() {
  return useQuery({
    queryKey: ["companies"],
    queryFn: () => apiFetch<Company[]>("/api/v1/companies"),
  });
}

export function usePriceAudit() {
  return useQuery({
    queryKey: ["price-audit"],
    queryFn: () =>
      apiFetch<
        Array<{
          id: number;
          ticker: string;
          company_name: string;
          old_price: string | null;
          new_price: string;
          delta_pct: string | null;
          changed_at: string;
          source: string;
        }>
      >("/api/v1/prices/audit"),
  });
}

export function usePriceHistory(companyId: number | null, days: number) {
  return useQuery({
    queryKey: ["price-history", companyId, days],
    queryFn: () => apiFetch<any[]>(`/api/v1/prices/history/${companyId}?days=${days}`),
    enabled: companyId !== null,
  });
}

export function useQuickPriceUpdate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: { company_id: number; price: string; entry_date: string }) =>
      fetchApiEnvelope<{
        ticker: string;
        old_price: string | null;
        new_price: string;
        delta_pct: string | null;
        entry_date: string;
        audit_id: number;
      }>("/api/v1/prices/quick", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["dashboard"] });
      qc.invalidateQueries({ queryKey: ["holdings"] });
      qc.invalidateQueries({ queryKey: ["companies"] });
      qc.invalidateQueries({ queryKey: ["price-audit"] });
    },
  });
}

export function useRevertPrice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (auditId: number) =>
      fetchApiEnvelope<{ reverted_to: string; new_audit_id: number }>(
        `/api/v1/prices/audit/${auditId}/revert`,
        { method: "POST" },
      ),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["dashboard"] });
      qc.invalidateQueries({ queryKey: ["holdings"] });
      qc.invalidateQueries({ queryKey: ["companies"] });
      qc.invalidateQueries({ queryKey: ["price-audit"] });
    },
  });
}

export function useBulkCsvImport() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ file, commit }: { file: File; commit: boolean }) => {
      const form = new FormData();
      form.append("file", file);
      form.append("commit", String(commit));
      return fetchApiEnvelope<Record<string, unknown>>("/api/v1/prices/bulk-csv", {
        method: "POST",
        body: form,
      });
    },
    onSuccess: (_data, variables) => {
      if (variables.commit) {
        qc.invalidateQueries({ queryKey: ["dashboard"] });
        qc.invalidateQueries({ queryKey: ["holdings"] });
        qc.invalidateQueries({ queryKey: ["companies"] });
        qc.invalidateQueries({ queryKey: ["price-audit"] });
      }
    },
  });
}

export function useUploadNGXPdf() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => {
      const form = new FormData();
      form.append("file", file);
      return fetchApiEnvelope<Record<string, unknown>>("/api/v1/prices/upload-pdf", {
        method: "POST",
        body: form,
      });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["dashboard"] });
      qc.invalidateQueries({ queryKey: ["holdings"] });
      qc.invalidateQueries({ queryKey: ["companies"] });
      qc.invalidateQueries({ queryKey: ["price-audit"] });
    },
  });
}

// ─── Companies Upload (F-NGX-COMPANIES) ──────────────────────────────────────

export function useUploadCompaniesPdf() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => {
      const form = new FormData();
      form.append("file", file);
      return fetchApiEnvelope<{
        summary: { total: number; inserted: number; updated: number; errors: string[] };
      }>("/api/v1/companies/upload-pdf", {
        method: "POST",
        body: form,
      });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["companies"] });
    },
  });
}

// ─── Registrars & Documents ──────────────────────────────────────────────────

export function useRegistrars() {
  return useQuery({
    queryKey: ["registrars"],
    queryFn: () => apiFetch<any[]>("/api/v1/registrars"),
  });
}

export function useAddRegistrar() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: any) =>
      fetchApiEnvelope("/api/v1/registrars", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["registrars"] }),
  });
}

export function useUpdateRegistrar() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...payload }: { id: number; [key: string]: any }) =>
      fetchApiEnvelope(`/api/v1/registrars/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["registrars"] }),
  });
}

export function useDeleteRegistrar() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) =>
      fetchApiEnvelope(`/api/v1/registrars/${id}`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["registrars"] }),
  });
}

export function useLinkCompany() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ registrarId, companyId }: { registrarId: number; companyId: number }) =>
      fetchApiEnvelope(`/api/v1/registrars/${registrarId}/companies/${companyId}`, {
        method: "POST",
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["registrars"] });
      qc.invalidateQueries({ queryKey: ["companies"] });
    },
  });
}

export function useUnlinkCompany() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ registrarId, companyId }: { registrarId: number; companyId: number }) =>
      fetchApiEnvelope(`/api/v1/registrars/${registrarId}/companies/${companyId}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["registrars"] });
      qc.invalidateQueries({ queryKey: ["companies"] });
    },
  });
}

export function useRegistrarRequirements(registrarId: number | null) {
  return useQuery({
    queryKey: ["registrar-requirements", registrarId],
    queryFn: () => apiFetch<any[]>(`/api/v1/registrars/${registrarId}/requirements`),
    enabled: !!registrarId,
  });
}

export function useAddRequirement() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ registrarId, ...payload }: { registrarId: number; [key: string]: any }) =>
      fetchApiEnvelope(`/api/v1/registrars/${registrarId}/requirements`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["registrars"] });
      qc.invalidateQueries({ queryKey: ["registrar-requirements", variables.registrarId] });
    },
  });
}

export function useUpdateRequirement() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, registrarId, ...payload }: { id: number; registrarId: number; [key: string]: any }) =>
      fetchApiEnvelope(`/api/v1/registrar-requirements/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["registrars"] });
      qc.invalidateQueries({ queryKey: ["registrar-requirements", variables.registrarId] });
    },
  });
}

export function useDeleteRequirement() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) =>
      fetchApiEnvelope(`/api/v1/registrar-requirements/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["registrars"] });
      qc.invalidateQueries({ queryKey: ["registrar-requirements"] });
    },
  });
}

export function useUploadDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ reqId, file, companyId, notes, onProgress }: { reqId: number; file: File; companyId?: number; notes?: string; onProgress?: (p: number) => void }) => {
      return new Promise<any>((resolve, reject) => {
        const form = new FormData();
        form.append("file", file);
        if (companyId) form.append("company_id", String(companyId));
        if (notes) form.append("notes", notes);
        
        const xhr = new XMLHttpRequest();
        xhr.open("POST", `/api/v1/registrar-requirements/${reqId}/documents`);
        xhr.withCredentials = true;
        
        if (onProgress) {
          xhr.upload.addEventListener("progress", (e) => {
            if (e.lengthComputable) {
              onProgress(Math.round((e.loaded / e.total) * 100));
            }
          });
        }
        
        xhr.onload = () => {
          if (xhr.status >= 200 && xhr.status < 300) {
             try {
               const json = JSON.parse(xhr.responseText);
               resolve(json);
             } catch(err) { resolve(xhr.responseText); }
          } else {
             reject(new Error(xhr.responseText || "Upload failed"));
          }
        };
        xhr.onerror = () => reject(new Error("Network Error"));
        xhr.send(form);
      });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["registrars"] });
      qc.invalidateQueries({ queryKey: ["registrar-requirements"] });
    },
  });
}

export function useUpdateDocumentStatus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ docId, status, notes }: { docId: number; status: string; notes?: string }) =>
      fetchApiEnvelope(`/api/v1/registrar-documents/${docId}/status`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status, notes }),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["registrars"] });
      qc.invalidateQueries({ queryKey: ["registrar-requirements"] });
    },
  });
}

export function useDeleteDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (docId: number) =>
      fetchApiEnvelope(`/api/v1/registrar-documents/${docId}`, { method: "DELETE" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["registrars"] });
      qc.invalidateQueries({ queryKey: ["registrar-requirements"] });
    },
  });
}

export function useDocumentHistory(reqId: number | null) {
  return useQuery({
    queryKey: ["document-history", reqId],
    queryFn: () => apiFetch<any[]>(`/api/v1/registrar-requirements/${reqId}/history`),
    enabled: !!reqId,
  });
}

// ─── Admin Users ──────────────────────────────────────────────────────────────

export interface AdminUser {
  id: number
  username: string
  name: string
  role: "admin" | "readonly"
  is_active: boolean
  created_at: string | null
  updated_at: string | null
  deleted_at: string | null
}

export function useAdminUsers(includeInactive = false) {
  return useQuery({
    queryKey: ["admin-users", includeInactive],
    queryFn: () =>
      fetch(`/api/v1/admin/users?include_inactive=${includeInactive}`, {
        credentials: "include",
      })
        .then(r => r.json())
        .then(r => r.data as AdminUser[]),
  })
}

export function useAdminCreateUser() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: { username: string; name: string; password: string; role: string }) =>
      fetch("/api/v1/admin/users", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }).then(r => r.json()),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-users"] })
    },
  })
}

export function useAdminUpdateUser() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: { name?: string; role?: string; is_active?: boolean } }) =>
      fetch(`/api/v1/admin/users/${id}`, {
        method: "PATCH",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }).then(r => r.json()),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-users"] })
    },
  })
}

export function useAdminResetPassword() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, newPassword }: { id: number; newPassword: string }) =>
      fetch(`/api/v1/admin/users/${id}/reset-password`, {
        method: "PUT",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ new_password: newPassword }),
      }).then(r => r.json()),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-users"] })
    },
  })
}

export function useAdminDeleteUser() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: number) =>
      fetch(`/api/v1/admin/users/${id}`, {
        method: "DELETE",
        credentials: "include",
      }).then(r => r.json()),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-users"] })
    },
  })
}
