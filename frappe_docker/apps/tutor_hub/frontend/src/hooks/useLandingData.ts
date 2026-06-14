import { useQuery } from "@tanstack/react-query";
import type { FrappeResponse, LandingData } from "@/types/landing";

// Frappe injects csrf_token into window via www/landing.html Jinja template.
// The "fetch" fallback is used in local dev where Frappe is not running.
declare global {
  interface Window {
    csrf_token: string;
  }
}

async function fetchLandingData(): Promise<LandingData> {
  const res = await fetch(
    "/api/method/tutor_hub.api.get_landing_page_data",
    {
      headers: {
        "Content-Type": "application/json",
        // "fetch" is a valid Frappe CSRF bypass for GET requests — fine for allow_guest=True
        "X-Frappe-CSRF-Token": window.csrf_token ?? "fetch",
      },
    }
  );

  if (!res.ok) {
    throw new Error(`Frappe API error: ${res.status} ${res.statusText}`);
  }

  // Frappe wraps all whitelist responses: { message: <your return value> }
  const json: FrappeResponse<LandingData> = await res.json();
  return json.message;
}

export function useLandingData() {
  return useQuery({
    queryKey: ["tutor-hub-landing"],
    queryFn: fetchLandingData,
    staleTime: 5 * 60 * 1000, // 5 min — content is static until DocTypes are wired up
    retry: 2,
  });
}
