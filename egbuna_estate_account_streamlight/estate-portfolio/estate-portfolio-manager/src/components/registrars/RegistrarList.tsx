import { useState } from "react";
import { useRegistrars } from "@/api/queries";
import { useAuthStore } from "@/store/authStore";
import { Button } from "@/components/ui/button";
import { Plus, Building2, FileWarning, Star } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { RegistrarModal } from "./RegistrarModal";

interface RegistrarListProps {
  selectedId: number | null;
  onSelect: (id: number) => void;
}

export function RegistrarList({ selectedId, onSelect }: RegistrarListProps) {
  const { data: registrars, isLoading, error } = useRegistrars();
  const isAdmin = useAuthStore((s) => s.isAdmin)();
  
  const [isAddOpen, setIsAddOpen] = useState(false);

  if (isLoading) {
    return <div className="p-4 text-center text-muted-foreground">Loading registrars...</div>;
  }

  if (error) {
    return <div className="p-4 text-center text-destructive">Error loading registrars.</div>;
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b p-4">
        <h2 className="text-lg font-semibold tracking-tight">Registrars</h2>
        {isAdmin && (
          <Button variant="outline" size="sm" className="h-8" onClick={() => setIsAddOpen(true)}>
            <Plus className="mr-2 h-4 w-4" /> Add
          </Button>
        )}
      </div>

      <ScrollArea className="flex-1">
        <div className="flex flex-col gap-2 p-3">
          {registrars?.map((r) => (
            <button
              key={r.id}
              onClick={() => onSelect(r.id)}
              className={cn(
                "flex flex-col gap-2 rounded-lg border p-3 text-left text-sm transition-all hover:bg-accent",
                selectedId === r.id ? "border-l-4 border-l-primary bg-accent/50" : "bg-card"
              )}
            >
              <div className="flex w-full items-start justify-between">
                <span className="font-semibold">{r.name}</span>
                {r.pending_document_count > 0 && (
                  <Badge variant="secondary" className="bg-amber-100 text-amber-700 hover:bg-amber-100/80">
                    {r.pending_document_count} pending
                  </Badge>
                )}
              </div>
              
              <div className="flex items-center gap-4 text-muted-foreground text-xs">
                <div className="flex items-center gap-1">
                  <Building2 className="h-3.5 w-3.5" />
                  <span>{r.linked_company_count} companies</span>
                </div>
                {r.response_rating && (
                  <div className="flex items-center gap-0.5">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <Star
                        key={i}
                        className={cn(
                          "h-3 w-3",
                          i < r.response_rating ? "fill-amber-400 text-amber-400" : "text-muted/50"
                        )}
                      />
                    ))}
                  </div>
                )}
              </div>
              <div className="flex flex-col gap-1 text-xs text-foreground/90 mt-2 font-medium">
                {r.phone && <div>📞 {r.phone}</div>}
                {r.email && <div className="truncate">✉️ {r.email}</div>}
                {r.address && <div className="truncate" title={r.address}>📍 {r.address}</div>}
                {!r.phone && !r.email && !r.address && (
                  <div className="italic text-muted-foreground/60 font-normal">No contact info</div>
                )}
              </div>
            </button>
          ))}
          {registrars?.length === 0 && (
            <div className="p-4 text-center text-sm text-muted-foreground">
              No registrars found.
            </div>
          )}
        </div>
      </ScrollArea>
      
      {isAddOpen && (
        <RegistrarModal isOpen={isAddOpen} onClose={() => setIsAddOpen(false)} />
      )}
    </div>
  );
}
