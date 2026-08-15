import { API_BASE_URL } from "./constants";

interface FrappeResponse<T = unknown> {
  message: T;
  exc?: string;
  exc_type?: string;
}

interface FrappeListResponse<T = unknown> {
  data: T[];
}

interface FrappeError {
  message: string;
  exc_type?: string;
  exc?: string;
  _server_messages?: string;
}

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(^| )${name}=([^;]+)`));
  return match ? decodeURIComponent(match[2]) : null;
}

function getCSRFToken(): string {
  return getCookie("csrf_token") || getCookie("X-Frappe-CSRF-Token") || "";
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMsg = `Request failed: ${response.status}`;
    try {
      const errBody: FrappeError = await response.json();
      if (errBody._server_messages) {
        try {
          const messages = JSON.parse(errBody._server_messages);
          if (Array.isArray(messages) && messages.length > 0) {
            const parsed = JSON.parse(messages[0]);
            errorMsg = parsed.message || errorMsg;
          }
        } catch {
          errorMsg = errBody._server_messages;
        }
      } else if (errBody.message) {
        errorMsg = errBody.message;
      } else if (errBody.exc) {
        errorMsg = errBody.exc;
      }
    } catch {
      // use default error message
    }
    throw new Error(errorMsg);
  }

  const body: FrappeResponse<T> = await response.json();
  return body.message;
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers: Record<string, string> = {
    Accept: "application/json",
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  const method = (options.method || "GET").toUpperCase();
  if (method !== "GET") {
    headers["X-Frappe-CSRF-Token"] = getCSRFToken();
  }

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: "include",
  });

  return handleResponse<T>(response);
}

export const frappeApi = {
  get<T>(endpoint: string): Promise<T> {
    return request<T>(endpoint, { method: "GET" });
  },

  post<T>(endpoint: string, data?: Record<string, unknown>): Promise<T> {
    return request<T>(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  put<T>(endpoint: string, data?: Record<string, unknown>): Promise<T> {
    return request<T>(endpoint, {
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  delete<T>(endpoint: string): Promise<T> {
    return request<T>(endpoint, { method: "DELETE" });
  },

  // Frappe list resources with filters
  async getList<T>(
    doctype: string,
    params?: {
      filters?: Record<string, unknown>[];
      fields?: string[];
      limit?: number;
      limit_start?: number;
      order_by?: string;
    }
  ): Promise<T[]> {
    const searchParams = new URLSearchParams();
    if (params?.filters) {
      searchParams.set("filters", JSON.stringify(params.filters));
    }
    if (params?.fields) {
      searchParams.set("fields", JSON.stringify(params.fields));
    }
    if (params?.limit !== undefined) {
      searchParams.set("limit_page_length", String(params.limit));
    }
    if (params?.limit_start !== undefined) {
      searchParams.set("limit_start", String(params.limit_start));
    }
    if (params?.order_by) {
      searchParams.set("order_by", params.order_by);
    }

    const query = searchParams.toString();
    const endpoint = `/api/resource/${doctype}${query ? `?${query}` : ""}`;
    const result = await request<FrappeListResponse<T>>(endpoint);
    return result.data;
  },

  // Frappe get single document
  async getDoc<T>(doctype: string, name: string): Promise<T> {
    const result = await request<{ data: T }>(
      `/api/resource/${doctype}/${encodeURIComponent(name)}`
    );
    return result.data;
  },

  // Frappe create document
  async createDoc<T>(doctype: string, data: Record<string, unknown>): Promise<T> {
    const result = await request<{ data: T }>(`/api/resource/${doctype}`, {
      method: "POST",
      body: JSON.stringify({ data: JSON.stringify(data) }),
    });
    return result.data;
  },

  // Frappe update document
  async updateDoc<T>(
    doctype: string,
    name: string,
    data: Record<string, unknown>
  ): Promise<T> {
    const result = await request<{ data: T }>(
      `/api/resource/${doctype}/${encodeURIComponent(name)}`,
      {
        method: "PUT",
        body: JSON.stringify({ data: JSON.stringify(data) }),
      }
    );
    return result.data;
  },

  // Frappe delete document
  async deleteDoc(doctype: string, name: string): Promise<void> {
    await request(`/api/resource/${doctype}/${encodeURIComponent(name)}`, {
      method: "DELETE",
    });
  },

  // Call custom Frappe method
  async call<T>(method: string, args?: Record<string, unknown>): Promise<T> {
    return request<T>(`/api/method/${method}`, {
      method: "POST",
      body: args ? JSON.stringify(args) : undefined,
    });
  },

  // Authentication
  async login(usr: string, pwd: string): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/api/method/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      credentials: "include",
      body: JSON.stringify({ usr, pwd }),
    });
    return response.json();
  },

  async logout(): Promise<void> {
    await fetch(`${API_BASE_URL}/api/method/logout`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Frappe-CSRF-Token": getCSRFToken(),
      },
      credentials: "include",
    });
  },

  async getSessionUser(): Promise<{
    message: { user: string; full_name: string; roles: string[] } | null;
  }> {
    try {
      const result = await request<{
        user: string;
        full_name: string;
        roles: string[];
      }>("/api/method/frappe.auth.get_logged_user");
      return { message: result };
    } catch {
      return { message: null };
    }
  },
};
