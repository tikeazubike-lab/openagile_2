import { createFileRoute } from "@tanstack/react-router";
import { Scale } from "lucide-react";
import { StubPage } from "@/components/shared/StubPage";

export const Route = createFileRoute("/_app/rebalancing")({
  component: () => (
    <StubPage
      title="Rebalancing"
      description="Sector targets, current allocation, and rebalance recommendations."
      Icon={Scale}
    />
  ),
});
