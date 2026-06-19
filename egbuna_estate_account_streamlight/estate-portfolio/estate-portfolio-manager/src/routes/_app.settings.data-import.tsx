import { createFileRoute } from "@tanstack/react-router";
import { Upload } from "lucide-react";
import { StubPage } from "@/components/shared/StubPage";

export const Route = createFileRoute("/_app/settings/data-import")({
  component: () => (
    <StubPage
      title="Data Import"
      description="Import CSV/Excel data for holdings, transactions, dividends."
      Icon={Upload}
    />
  ),
});
