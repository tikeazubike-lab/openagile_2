import { useState, useEffect } from "react";
import { useAddRegistrar, useUpdateRegistrar } from "@/api/queries";
import { useUIStore } from "@/store/uiStore";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Plus, Trash2 } from "lucide-react";

interface ContactField {
  field_type: "phone" | "email" | "address" | "website" | "other";
  field_value: string;
  label: string;
  sort_order: number;
}

interface Props {
  isOpen: boolean;
  onClose: () => void;
  existingData?: any; // If provided, we are in edit mode
}

export function RegistrarModal({ isOpen, onClose, existingData }: Props) {
  const addRegistrar = useAddRegistrar();
  const updateRegistrar = useUpdateRegistrar();
  const addToast = useUIStore((s) => s.addToast);
  
  const [name, setName] = useState("");
  const [responseRating, setResponseRating] = useState<string>("none");
  const [notes, setNotes] = useState("");
  
  const [contactFields, setContactFields] = useState<ContactField[]>([]);

  useEffect(() => {
    if (existingData && isOpen) {
      setName(existingData.name || "");
      setResponseRating(existingData.response_rating ? String(existingData.response_rating) : "none");
      setNotes(existingData.notes || "");
      if (existingData.contact_fields && Array.isArray(existingData.contact_fields)) {
        setContactFields(
          existingData.contact_fields.map((cf: any) => ({
            field_type: cf.field_type,
            field_value: cf.field_value,
            label: cf.label || "",
            sort_order: cf.sort_order || 0,
          }))
        );
      } else {
        // Fallback for old data structure if any
        const legacyFields: ContactField[] = [];
        let order = 1;
        if (existingData.email) legacyFields.push({ field_type: "email", field_value: existingData.email, label: "", sort_order: order++ });
        if (existingData.phone) legacyFields.push({ field_type: "phone", field_value: existingData.phone, label: "", sort_order: order++ });
        if (existingData.website) legacyFields.push({ field_type: "website", field_value: existingData.website, label: "", sort_order: order++ });
        if (existingData.address) legacyFields.push({ field_type: "address", field_value: existingData.address, label: "", sort_order: order++ });
        setContactFields(legacyFields);
      }
    } else if (isOpen) {
      setName("");
      setResponseRating("none");
      setNotes("");
      setContactFields([
        { field_type: "phone", field_value: "", label: "Main", sort_order: 1 },
        { field_type: "email", field_value: "", label: "Support", sort_order: 2 }
      ]);
    }
  }, [existingData, isOpen]);

  const handleAddField = () => {
    setContactFields([
      ...contactFields,
      { field_type: "other", field_value: "", label: "", sort_order: contactFields.length + 1 }
    ]);
  };

  const handleRemoveField = (index: number) => {
    const newFields = [...contactFields];
    newFields.splice(index, 1);
    // update sort_order
    newFields.forEach((cf, idx) => cf.sort_order = idx + 1);
    setContactFields(newFields);
  };

  const updateField = (index: number, key: keyof ContactField, value: string) => {
    const newFields = [...contactFields];
    newFields[index] = { ...newFields[index], [key]: value };
    setContactFields(newFields);
  };

  const handleSave = () => {
    if (!name) {
      addToast({ title: "Validation Error", description: "Name is required.", type: "error" });
      return;
    }

    // Filter out empty fields
    const validFields = contactFields.filter(f => f.field_value.trim() !== "");

    const payload = {
      name,
      response_rating: responseRating !== "none" ? Number(responseRating) : undefined,
      notes: notes || undefined,
      contact_fields: validFields,
    };

    if (existingData) {
      updateRegistrar.mutate(
        { id: existingData.id, ...payload },
        {
          onSuccess: () => {
            addToast({ title: "Registrar updated", type: "success" });
            onClose();
          },
          onError: (err: any) => {
            addToast({ title: "Failed to update", description: err.message, type: "error" });
          }
        }
      );
    } else {
      addRegistrar.mutate(
        payload,
        {
          onSuccess: () => {
            addToast({ title: "Registrar created", type: "success" });
            onClose();
          },
          onError: (err: any) => {
            addToast({ title: "Failed to create", description: err.message, type: "error" });
          }
        }
      );
    }
  };

  const isPending = addRegistrar.isPending || updateRegistrar.isPending;

  const placeholderFor = (type: string) => ({
    phone:   "e.g. 0800-555-0100",
    email:   "e.g. info@registrar.com.ng",
    address: "e.g. 2 Broad Street, Lagos",
    website: "e.g. https://registrar.com.ng",
    other:   "e.g. WhatsApp: 080...",
  }[type] ?? "Enter value");

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div className="relative w-full max-w-lg mx-4 bg-[var(--bg-surface)] border border-[var(--border)] rounded-xl shadow-[var(--shadow-modal)] max-h-[90vh] overflow-y-auto p-6">
        <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4">
          {existingData ? "Edit Registrar" : "Add Registrar"}
        </h2>
        
        <div className="grid gap-4">
          <div className="grid gap-2">
            <Label htmlFor="name">Name *</Label>
            <Input id="name" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. First Registrars Nigeria Ltd" className="bg-transparent" />
          </div>

          <div className="grid gap-2 mt-2">
            <div className="flex justify-between items-center mb-2">
              <Label>Contact Details</Label>
              <Button type="button" variant="outline" size="sm" onClick={handleAddField} className="h-8 gap-1">
                <Plus className="w-3.5 h-3.5" /> Add Detail
              </Button>
            </div>
            
            <div className="flex flex-col gap-3">
              {contactFields.map((field, index) => (
                <div key={index} className="grid grid-cols-[80px_1fr_32px] gap-2 items-center">
                  <span className="text-xs font-medium px-2 py-1 rounded-full bg-[var(--bg-subtle)] text-[var(--text-secondary)] text-center capitalize">
                    {field.field_type}
                  </span>

                  <input
                    value={field.field_value}
                    onChange={e => updateField(index, "field_value", e.target.value)}
                    placeholder={placeholderFor(field.field_type)}
                    className="h-9 px-3 rounded-lg border border-[var(--border)] bg-[var(--bg-surface)] text-[var(--text-primary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--accent-lavender)]"
                  />

                  <button
                    onClick={() => handleRemoveField(index)}
                    className="w-8 h-8 flex items-center justify-center text-[var(--text-muted)] hover:text-[var(--accent-red)] rounded-lg hover:bg-[var(--bg-subtle)] transition-colors"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="grid gap-2 mt-2">
            <Label htmlFor="rating">Response Rating (1-5)</Label>
            <Select value={responseRating} onValueChange={setResponseRating}>
              <SelectTrigger className="bg-transparent border-[var(--border)] text-[var(--text-primary)]">
                <SelectValue placeholder="Select rating" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">-- Not Rated --</SelectItem>
                <SelectItem value="1">1 Star (Very Poor)</SelectItem>
                <SelectItem value="2">2 Stars (Poor)</SelectItem>
                <SelectItem value="3">3 Stars (Average)</SelectItem>
                <SelectItem value="4">4 Stars (Good)</SelectItem>
                <SelectItem value="5">5 Stars (Excellent)</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="grid gap-2 mt-2">
            <Label htmlFor="notes">Internal Notes</Label>
            <Textarea 
              id="notes" 
              value={notes} 
              onChange={(e) => setNotes(e.target.value)} 
              placeholder="Internal operational notes..."
              className="bg-transparent border-[var(--border)] text-[var(--text-primary)] min-h-[80px]"
            />
          </div>
        </div>
        
        <div className="flex justify-end gap-2 mt-6 pt-4 border-t border-[var(--border)]">
          <Button variant="outline" onClick={onClose} disabled={isPending} className="bg-transparent border-[var(--border)] text-[var(--text-primary)] hover:bg-[var(--bg-subtle)]">
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={isPending} className="bg-[var(--accent-lavender)] text-[#1A1A1A] hover:brightness-110">
            {isPending ? "Saving..." : "Save Registrar"}
          </Button>
        </div>
      </div>
    </div>
  );
}
