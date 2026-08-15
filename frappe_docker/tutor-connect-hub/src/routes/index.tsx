import { createBrowserRouter, Navigate } from "react-router-dom";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Home } from "./Home";
import { Login } from "./Login";
import { RegisterStudent } from "./RegisterStudent";
import { RegisterTutor } from "./RegisterTutor";

// Owner pages
import { OwnerDashboard } from "./owner/Dashboard";
import { OwnerTutors } from "./owner/Tutors";
import { OwnerPayments } from "./owner/Payments";
import { OwnerSettings } from "./owner/Settings";

// Tutor pages
import { TutorDashboard } from "./tutor/Dashboard";
import { TutorSchedule } from "./tutor/Schedule";
import { TutorSessions } from "./tutor/Sessions";
import { TutorEarnings } from "./tutor/Earnings";

// Student pages
import { StudentDashboard } from "./student/Dashboard";
import { StudentBrowse } from "./student/Browse";
import { StudentBook } from "./student/Book";
import { StudentSessions } from "./student/Sessions";
import { StudentPayments } from "./student/Payments";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Home />,
  },
  {
    path: "/login",
    element: <Login />,
  },
  {
    path: "/register/student",
    element: <RegisterStudent />,
  },
  {
    path: "/register/tutor",
    element: <RegisterTutor />,
  },
  {
    path: "/owner",
    element: <DashboardLayout />,
    children: [
      { index: true, element: <OwnerDashboard /> },
      { path: "tutors", element: <OwnerTutors /> },
      { path: "payments", element: <OwnerPayments /> },
      { path: "settings", element: <OwnerSettings /> },
    ],
  },
  {
    path: "/tutor",
    element: <DashboardLayout />,
    children: [
      { index: true, element: <TutorDashboard /> },
      { path: "schedule", element: <TutorSchedule /> },
      { path: "sessions", element: <TutorSessions /> },
      { path: "earnings", element: <TutorEarnings /> },
    ],
  },
  {
    path: "/student",
    element: <DashboardLayout />,
    children: [
      { index: true, element: <StudentDashboard /> },
      { path: "browse", element: <StudentBrowse /> },
      { path: "book", element: <StudentBook /> },
      { path: "sessions", element: <StudentSessions /> },
      { path: "payments", element: <StudentPayments /> },
    ],
  },
  {
    path: "*",
    element: <Navigate to="/" replace />,
  },
]);
