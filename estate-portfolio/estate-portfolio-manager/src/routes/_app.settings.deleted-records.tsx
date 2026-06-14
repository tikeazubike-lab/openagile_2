import { createFileRoute } from "@tanstack/react-router";
import { Trash2 } from "lucide-react";
import { StubPage } from "@/components/shared/StubPage";

export const Route = createFileRoute("/_app/settings/deleted-records")({
  component: () => (
    <StubPage
      title="Deleted Records"
      description="Recover soft-deleted holdings, transactions, dividends."
      Icon={Trash2}
    />
  ),
});
