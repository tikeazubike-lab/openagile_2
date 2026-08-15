export const API_BASE_URL =
  import.meta.env.VITE_FRAPPE_URL || "https://tutor.zubbystudio.site";

export const ROLES = {
  STUDENT: "Tutor Hub Student",
  TUTOR: "Tutor Hub Tutor",
  OWNER: "Tutor Hub Owner",
  ADMIN: "Administrator",
} as const;

export type Role = (typeof ROLES)[keyof typeof ROLES];

export const SESSION_STATUS = {
  PENDING: "Pending",
  CONFIRMED: "Confirmed",
  IN_PROGRESS: "In Progress",
  COMPLETED: "Completed",
  CANCELLED: "Cancelled",
  NO_SHOW: "No Show",
} as const;

export const PAYMENT_STATUS = {
  PENDING: "Pending",
  PAID: "Paid",
  FAILED: "Failed",
  REFUNDED: "Refunded",
} as const;

export const SUBJECTS = [
  "Mathematics",
  "Physics",
  "Chemistry",
  "Biology",
  "English",
  "Computer Science",
  "Economics",
  "Accounting",
  "French",
  "Yoruba",
  "History",
  "Geography",
] as const;
