import { useState } from "react";
import { RegistrarList } from "./RegistrarList";
import { RegistrarDetails } from "./RegistrarDetails";
import { RegistrarsDashboard } from "./RegistrarsDashboard";

export function RegistrarsLayout() {
  const [selectedId, setSelectedId] = useState<number | null>(null);

  return (
    // F-026: scrollable column so the read-only dashboard can sit above the
    // list/details layout, which keeps its original full-viewport behaviour.
    <div className="flex h-[calc(100vh-4rem)] flex-col overflow-y-auto bg-background">
      <RegistrarsDashboard />

      <div className="flex h-[calc(100vh-4rem)] flex-col md:flex-row overflow-hidden bg-background">
        {/* Left Panel */}
        <div className="w-full md:w-[320px] border-r flex flex-col">
          <RegistrarList 
            selectedId={selectedId} 
            onSelect={(id) => setSelectedId(id)} 
          />
        </div>

        {/* Right Panel */}
        <div className="flex-1 overflow-y-auto bg-muted/20">
          {selectedId ? (
            <RegistrarDetails registrarId={selectedId} />
          ) : (
            <div className="flex h-full items-center justify-center text-muted-foreground">
              Select a registrar to view details
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
