import { createFileRoute } from "@tanstack/react-router";
import { Building2 } from "lucide-react";
import { StubPage } from "@/components/shared/StubPage";

export const Route = createFileRoute("/_app/companies")({
  component: () => (
    <StubPage
      title="Companies"
      description="Manage NGX-listed companies, sectors, and registrar links."
      Icon={Building2}
    />
  ),
});
