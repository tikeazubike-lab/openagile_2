import { createFileRoute } from "@tanstack/react-router";
import { Eye } from "lucide-react";
import { StubPage } from "@/components/shared/StubPage";

export const Route = createFileRoute("/_app/watchlist")({
  component: () => (
    <StubPage
      title="Watchlist"
      description="Stocks you are watching with target prices and gap to target."
      Icon={Eye}
    />
  ),
});
