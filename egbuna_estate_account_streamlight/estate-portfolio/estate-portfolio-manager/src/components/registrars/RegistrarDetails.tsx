import { useState } from "react";
import { useRegistrars, useUnlinkCompany, useDeleteRegistrar } from "@/api/queries";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Edit, Mail, Phone, MapPin, Globe, Plus, X, Info } from "lucide-react";
import { Link } from "@tanstack/react-router";
import { Badge } from "@/components/ui/badge";
import { RegistrarRequirements } from "./RegistrarRequirements";
import { RegistrarModal } from "./RegistrarModal";
import { LinkCompanyModal } from "./LinkCompanyModal";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { useAuthStore } from "@/store/authStore";
import { useNavigate } from "@tanstack/react-router";

export function RegistrarDetails({ registrarId }: { registrarId: number }) {
  const { data: registrars } = useRegistrars();
  const { mutate: unlinkCompany } = useUnlinkCompany();
  const deleteRegistrarMutation = useDeleteRegistrar();
  const { user } = useAuthStore();
  const isAdmin = user?.role === "admin";
  const navigate = useNavigate();
  
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isLinkOpen, setIsLinkOpen] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const registrar = registrars?.find((r) => r.id === registrarId);

  if (!registrar) return null;

  const renderIcon = (type: string) => {
    switch (type) {
      case "email": return <Mail className="h-4 w-4" />;
      case "phone": return <Phone className="h-4 w-4" />;
      case "website": return <Globe className="h-4 w-4" />;
      case "address": return <MapPin className="h-4 w-4 shrink-0" />;
      default: return <Info className="h-4 w-4" />;
    }
  };

  const renderFieldValue = (type: string, value: string) => {
    if (type === "website") {
      return (
        <a href={value} target="_blank" rel="noreferrer" className="text-primary hover:underline truncate">
          {value}
        </a>
      );
    }
    if (type === "email") {
      return (
        <a href={`mailto:${value}`} className="text-primary hover:underline truncate">
          {value}
        </a>
      );
    }
    if (type === "phone") {
      return (
        <a href={`tel:${value}`} className="text-primary hover:underline truncate">
          {value}
        </a>
      );
    }
    return <span>{value}</span>;
  };

  const legacyContactFields = [];
  if (registrar.email) legacyContactFields.push({ field_type: "email", field_value: registrar.email, sort_order: 1 });
  if (registrar.phone) legacyContactFields.push({ field_type: "phone", field_value: registrar.phone, sort_order: 2 });
  if (registrar.website) legacyContactFields.push({ field_type: "website", field_value: registrar.website, sort_order: 3 });
  if (registrar.address) legacyContactFields.push({ field_type: "address", field_value: registrar.address, sort_order: 4 });

  // Use contact_fields if available, else fallback to legacy fields (if any)
  const fieldsToRender = (registrar.contact_fields && registrar.contact_fields.length > 0)
    ? registrar.contact_fields
    : legacyContactFields;

  // Sort them
  fieldsToRender.sort((a: any, b: any) => (a.sort_order || 0) - (b.sort_order || 0));

  return (
    <div className="flex flex-col gap-6 p-4 md:p-6 max-w-5xl mx-auto">
      {/* Details Card */}
      <Card>
        <CardHeader className="flex flex-row items-center gap-2 space-y-0 pb-2">
          <CardTitle className="text-2xl font-bold flex-1">{registrar.name}</CardTitle>
          {isAdmin && (
            <>
              <Button variant="ghost" size="icon" onClick={() => setIsEditOpen(true)}>
                <Edit className="h-4 w-4" />
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => setShowDeleteConfirm(true)}
                className="text-[var(--accent-red)] border-[var(--accent-red)] hover:bg-[var(--accent-red)] hover:text-white"
              >
                Delete
              </Button>
            </>
          )}
        </CardHeader>
        <CardContent>
          {fieldsToRender.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm mt-4">
              {fieldsToRender.map((cf: any, i: number) => (
                <div key={i} className={`flex items-start gap-2 text-muted-foreground ${cf.field_type === 'address' ? 'md:col-span-2' : ''}`}>
                  <div className="mt-0.5 shrink-0">
                    {renderIcon(cf.field_type)}
                  </div>
                  <div className="flex flex-col">
                    {cf.label && <span className="text-[11px] font-semibold text-muted-foreground uppercase">{cf.label}</span>}
                    <div className="break-all">{renderFieldValue(cf.field_type, cf.field_value)}</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-muted-foreground mt-4">No contact details provided.</div>
          )}
        </CardContent>
      </Card>

      {/* Linked Companies */}
      {(registrar.linked_companies?.length > 0 || isAdmin) && (
        <Card>
          <CardHeader className="pb-3 flex flex-row items-center justify-between">
            <CardTitle className="text-lg">Linked Companies</CardTitle>
            {isAdmin && (
              <Button variant="outline" size="sm" onClick={() => setIsLinkOpen(true)}>
                <Plus className="mr-2 h-3 w-3" /> Link
              </Button>
            )}
          </CardHeader>
          <CardContent>
            {registrar.linked_companies && registrar.linked_companies.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {registrar.linked_companies.map((c: any) => (
                  <div key={c.id} className="relative inline-block">
                    <Link to="/companies" className="transition-transform hover:scale-105 inline-block">
                      <Badge variant="secondary" className={`bg-primary/10 text-primary hover:bg-primary/20 ${isAdmin ? 'pr-6' : ''}`}>
                        {c.ticker}
                      </Badge>
                    </Link>
                    {isAdmin && (
                      <button
                        onClick={(e) => { 
                          e.preventDefault(); 
                          if(confirm(`Unlink ${c.ticker}?`)) {
                            unlinkCompany({ registrarId, companyId: c.id });
                          }
                        }}
                        className="absolute right-1 top-1/2 -translate-y-1/2 text-primary hover:text-destructive bg-primary/10 rounded-full p-0.5"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-muted-foreground">No linked companies.</div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Requirements & Documents */}
      <RegistrarRequirements registrarId={registrarId} />
      
      {isEditOpen && (
        <RegistrarModal isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} existingData={registrar} />
      )}
      
      {isLinkOpen && (
        <LinkCompanyModal 
          isOpen={isLinkOpen} 
          onClose={() => setIsLinkOpen(false)} 
          registrarId={registrarId} 
          linkedCompanyIds={registrar.linked_companies?.map((c: any) => c.id) || []} 
        />
      )}

      <AlertDialog open={showDeleteConfirm} onOpenChange={setShowDeleteConfirm}>
        <AlertDialogContent className="bg-popover text-popover-foreground">
          <AlertDialogHeader>
            <AlertDialogTitle>Delete {registrar.name}?</AlertDialogTitle>
            <AlertDialogDescription>
              This will remove all linked requirements and documents.
              {registrar.linked_companies && registrar.linked_companies.length > 0
                ? ` ${registrar.linked_companies.length} companies will be unlinked.`
                : ''}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              onClick={() => {
                deleteRegistrarMutation.mutate(registrar.id);
                setShowDeleteConfirm(false);
              }}
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

