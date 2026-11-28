import { useState } from "react";
import { RegistrarList } from "./RegistrarList";
import { RegistrarDetails } from "./RegistrarDetails";
import { RegistrarsDashboard } from "./RegistrarsDashboard";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

// F-026 §9 (2026-11-24, Product Owner choice "2"): /registrars uses tabs so the
// registrar list keeps its full pre-F-026 height (stacking the dashboard above
// it squeezed the list to 32px). Registrars is first and default; the Dashboard
// content mounts only when selected (Radix default, no forceMount), so its
// queries run on demand. Tab state is local (no URL parameter); selectedId is
// kept here so the selected registrar survives a tab switch.
export function RegistrarsLayout() {
  const [selectedId, setSelectedId] = useState<number | null>(null);

  return (
    <Tabs
      defaultValue="registrars"
      className="flex h-[calc(100vh-4rem)] flex-col bg-background"
    >
      <TabsList className="shrink-0 mt-2 ml-2">
        <TabsTrigger value="registrars">Registrars</TabsTrigger>
        <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
      </TabsList>

      {/* Registrars tab: the ORIGINAL pre-F-026 list/details layout, filling
          the remaining height. */}
      <TabsContent value="registrars" className="flex-1 min-h-0 mt-0">
        <div className="flex h-full flex-col md:flex-row overflow-hidden">
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
      </TabsContent>

      {/* Dashboard tab: unmounts when inactive, so the two dashboard queries
          only run once the tab is opened. */}
      <TabsContent
        value="dashboard"
        className="flex-1 min-h-0 overflow-y-auto mt-0"
      >
        <RegistrarsDashboard />
      </TabsContent>
    </Tabs>
  );
}
