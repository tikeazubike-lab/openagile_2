import { createFileRoute } from "@tanstack/react-router";
import { RegistrarsLayout } from "@/components/registrars/RegistrarsLayout";

export const Route = createFileRoute("/_app/registrars")({
  component: () => <RegistrarsLayout />,
});
