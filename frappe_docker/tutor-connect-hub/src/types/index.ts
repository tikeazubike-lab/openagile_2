export interface Tutor {
  name: string;
  owner: string;
  creation: string;
  modified: string;
  full_name: string;
  email: string;
  phone: string;
  bio: string;
  subjects: string;
  hourly_rate: number;
  experience_years: number;
  qualifications: string;
  rating: number;
  total_sessions: number;
  is_active: boolean;
  profile_image?: string;
  availability_schedule?: string;
}

export interface Student {
  name: string;
  owner: string;
  creation: string;
  modified: string;
  full_name: string;
  email: string;
  phone: string;
  grade_level?: string;
  preferred_subjects?: string;
}

export interface Session {
  name: string;
  owner: string;
  creation: string;
  modified: string;
  student: string;
  student_name: string;
  tutor: string;
  tutor_name: string;
  subject: string;
  session_date: string;
  start_time: string;
  end_time: string;
  duration_hours: number;
  status: "Pending" | "Confirmed" | "In Progress" | "Completed" | "Cancelled" | "No Show";
  hourly_rate: number;
  total_amount: number;
  platform_fee: number;
  notes?: string;
  meeting_link?: string;
  rating?: number;
  feedback?: string;
}

export interface Payment {
  name: string;
  owner: string;
  creation: string;
  modified: string;
  session: string;
  student: string;
  student_name: string;
  tutor: string;
  tutor_name: string;
  amount: number;
  platform_fee: number;
  tutor_payout: number;
  status: "Pending" | "Paid" | "Failed" | "Refunded";
  payment_date?: string;
  payment_method?: string;
  transaction_reference?: string;
}

export interface TimeSlot {
  day_of_week: string;
  start_time: string;
  end_time: string;
  is_available: boolean;
}

export interface TutorAvailability {
  name: string;
  tutor: string;
  slots: TimeSlot[];
}

export interface DashboardStats {
  total_sessions: number;
  completed_sessions: number;
  upcoming_sessions: number;
  total_revenue: number;
  active_tutors: number;
  active_students: number;
  completion_rate: number;
  average_rating: number;
}

export interface RevenueDataPoint {
  month: string;
  revenue: number;
  sessions: number;
}

export interface User {
  name: string;
  email: string;
  full_name: string;
  roles: string[];
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  roles: string[];
}
