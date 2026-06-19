import { useState } from "react";
import { useCompanies, useLinkCompany } from "@/api/queries";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";

interface LinkCompanyModalProps {
  isOpen: boolean;
  onClose: () => void;
  registrarId: number;
  linkedCompanyIds: number[];
}

export function LinkCompanyModal({ isOpen, onClose, registrarId, linkedCompanyIds }: LinkCompanyModalProps) {
  const { data: companies, isLoading } = useCompanies();
  const { mutate: linkCompany, isPending } = useLinkCompany();
  const [selectedCompanyId, setSelectedCompanyId] = useState<string>("");

  // Filter out companies that are already linked
  const availableCompanies = companies?.filter(c => !linkedCompanyIds.includes(c.id)) || [];

  const handleLink = () => {
    if (!selectedCompanyId) return;
    linkCompany(
      { registrarId, companyId: parseInt(selectedCompanyId, 10) },
      {
        onSuccess: () => {
          onClose();
        },
      }
    );
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Link Company</DialogTitle>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Select Company</label>
            {isLoading ? (
              <div className="text-sm text-muted-foreground">Loading companies...</div>
            ) : availableCompanies.length === 0 ? (
              <div className="text-sm text-muted-foreground border rounded-md p-2 bg-muted/20">
                All available companies are already linked.
              </div>
            ) : (
              <select
                className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                value={selectedCompanyId}
                onChange={(e) => setSelectedCompanyId(e.target.value)}
              >
                <option value="">-- Choose a company --</option>
                {availableCompanies.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.ticker} - {c.name}
                  </option>
                ))}
              </select>
            )}
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={isPending}>
            Cancel
          </Button>
          <Button onClick={handleLink} disabled={!selectedCompanyId || isPending}>
            {isPending ? "Linking..." : "Link Company"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
