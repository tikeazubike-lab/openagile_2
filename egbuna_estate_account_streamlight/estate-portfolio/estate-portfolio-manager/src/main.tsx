import React from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider } from "@tanstack/react-router";
import "./styles.css";
import { getRouter } from "./router";

// EPM Phase 2 — SPA entry point.
// The router is created once here and passed to RouterProvider.
// QueryClientProvider and theme initialisation live in __root.tsx.

const router = getRouter();

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
);
