// Spec: F-026-email-reminder-infrastructure.md | F-026b settings UI (HO-159 item 6) |
// Then the reminder settings page unwraps the { data, meta, error } envelope for the
// test-send response and the reminder log, and shows an error state (not the empty
// state) when the log query fails.
// NOTE: no @testing-library/jest-dom import (package missing — AUDIT R10);
// plain vitest matchers + Testing Library queries only.
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { TestSendCard, ReminderLogCard } from "../_app.settings.registrars";

function jsonResponse(body: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as Response;
}

function renderWithQueryClient(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

describe("Registrar reminder settings (F-026b)", () => {
  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  // Spec: F-026-email-reminder-infrastructure.md | AC-5 | Then test-send success
  // unwraps the envelope and shows the recipient from data.recipient
  it("unwraps the test-send envelope and shows the recipient", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        jsonResponse({
          data: { status: "sent", recipient: "ops@example.com" },
          meta: {},
          error: null,
        }),
      ),
    );

    renderWithQueryClient(<TestSendCard />);
    fireEvent.click(screen.getByRole("button", { name: /send test email/i }));

    // Before the fix this rendered "Sent to undefined" (envelope not unwrapped).
    expect(await screen.findByText("Sent to ops@example.com")).toBeTruthy();
  });

  // Supporting test (not a spec AC): a failing reminder-log query shows the error
  // state instead of the empty-state message. F-026b AC-6 is the sanitized 502 on
  // test-send, not this log-view state; no AC covers this UI state.
  it("shows an error state when the reminder log query fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => jsonResponse({ detail: "smtp relay down" }, 500)),
    );

    renderWithQueryClient(<ReminderLogCard />);

    // Before the fix a 4xx/5xx rendered the misleading "No reminders sent yet."
    expect(await screen.findByText(/Failed to load reminder log/)).toBeTruthy();
    expect(screen.queryByText("No reminders sent yet.")).toBeNull();
  });

  // Spec: F-026-email-reminder-infrastructure.md | AC-5 | Then the reminder log rows
  // render from the as-built nested envelope { data: { data, meta } }
  it("unwraps the reminder log envelope and renders rows", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        jsonResponse({
          // As built in registrars.py: rows + pagination live inside the envelope's data.
          data: {
            data: [
              {
                id: 1,
                requirement_id: 21,
                requirement_title: "CAC Form 7",
                reminder_type: "overdue",
                recipient_email: "ops@example.com",
                delivery_status: "sent",
                error_detail: null,
                sent_at: "2026-11-20T10:00:00",
              },
            ],
            meta: { total: 1, page: 1, page_size: 10, total_pages: 1 },
          },
          meta: {},
          error: null,
        }),
      ),
    );

    renderWithQueryClient(<ReminderLogCard />);

    // Before the fix the row list was read one envelope level too high and the
    // table crashed / stayed empty.
    expect(await screen.findByText("CAC Form 7")).toBeTruthy();
    expect(screen.getByText("overdue")).toBeTruthy();
    expect(screen.getByText("sent")).toBeTruthy();
    expect(screen.queryByText("No reminders sent yet.")).toBeNull();
  });
});
