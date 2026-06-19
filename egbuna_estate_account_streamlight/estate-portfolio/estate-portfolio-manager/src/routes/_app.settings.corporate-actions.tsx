import { createFileRoute } from "@tanstack/react-router";
import { Landmark } from "lucide-react";
import { StubPage } from "@/components/shared/StubPage";

export const Route = createFileRoute("/_app/settings/corporate-actions")({
  component: () => (
    <StubPage
      title="Corporate Actions"
      description="Bonuses, rights issues, splits, and mergers."
      Icon={Landmark}
    />
  ),
});
