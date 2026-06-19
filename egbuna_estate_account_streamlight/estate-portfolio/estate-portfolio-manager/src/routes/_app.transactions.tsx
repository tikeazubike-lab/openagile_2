import { createFileRoute } from "@tanstack/react-router";
import { ArrowLeftRight } from "lucide-react";
import { StubPage } from "@/components/shared/StubPage";

export const Route = createFileRoute("/_app/transactions")({
  component: () => (
    <StubPage
      title="Transactions"
      description="All buys, sells, bonus issues, and rights — with drafts."
      Icon={ArrowLeftRight}
    />
  ),
});
