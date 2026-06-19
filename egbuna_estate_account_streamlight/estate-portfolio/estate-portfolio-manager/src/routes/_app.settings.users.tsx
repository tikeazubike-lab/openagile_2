import { createFileRoute } from "@tanstack/react-router";
import { Users } from "lucide-react";
import { StubPage } from "@/components/shared/StubPage";

export const Route = createFileRoute("/_app/settings/users")({
  component: () => (
    <StubPage
      title="User Management"
      description="Add admin or read-only users, reset passwords."
      Icon={Users}
    />
  ),
});
