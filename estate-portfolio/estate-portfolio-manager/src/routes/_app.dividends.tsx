import { createFileRoute } from "@tanstack/react-router";
import { Coins } from "lucide-react";
import { StubPage } from "@/components/shared/StubPage";

export const Route = createFileRoute("/_app/dividends")({
  component: () => (
    <StubPage
      title="Dividends"
      description="Track dividend history, DRIP, and lifetime totals."
      Icon={Coins}
    />
  ),
});
