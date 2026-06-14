import { createFileRoute } from "@tanstack/react-router";
import { TrendingDown } from "lucide-react";
import { StubPage } from "@/components/shared/StubPage";

export const Route = createFileRoute("/_app/nav-history")({
  component: () => (
    <StubPage
      title="NAV History"
      description="Net asset value over time, with portfolio vs invested."
      Icon={TrendingDown}
    />
  ),
});
