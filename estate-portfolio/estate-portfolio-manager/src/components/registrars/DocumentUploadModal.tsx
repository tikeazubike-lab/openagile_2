import { useState } from "react";
import { useUploadDocument, useCompanies } from "@/api/queries";
import { useUIStore } from "@/store/uiStore";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";

interface Props {
  reqId: number;
  isOpen: boolean;
  onClose: () => void;
}

export function DocumentUploadModal({ reqId, isOpen, onClose }: Props) {
  const uploadDoc = useUploadDocument();
  const { data: companies } = useCompanies();
  const addToast = useUIStore((s) => s.addToast);
  
  const [file, setFile] = useState<File | null>(null);
  const [companyId, setCompanyId] = useState<string>("none");
  const [notes, setNotes] = useState("");
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      if (selected.size > 20 * 1024 * 1024) {
        setUploadError(`File too large: ${(selected.size / 1024 / 1024).toFixed(1)}MB. Maximum is 20MB.`);
        setFile(null);
        setUploadProgress(null);
        e.target.value = ""; // Reset input
        return;
      }
      setUploadError(null);
      setFile(selected);
    }
  };

  const handleUpload = () => {
    if (!file) return;

    if (file.size > 20 * 1024 * 1024) {
      setUploadError(`File too large: ${(file.size / 1024 / 1024).toFixed(1)}MB. Maximum is 20MB.`);
      return;
    }
    
    uploadDoc.mutate(
      {
        reqId,
        file,
        companyId: companyId !== "none" ? Number(companyId) : undefined,
        notes: notes || undefined,
        onProgress: (p) => setUploadProgress(p)
      },
      {
        onSuccess: () => {
          addToast({ title: "Document uploaded successfully", type: "success" });
          onClose();
        },
        onError: (err) => {
          setUploadError(err.message);
          setUploadProgress(null);
          addToast({ title: "Upload failed", description: err.message, type: "error" });
        }
      }
    );
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Upload Document</DialogTitle>
        </DialogHeader>
        
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="file">File (PDF, JPG, PNG)</Label>
            <Input id="file" type="file" accept=".pdf,.jpg,.jpeg,.png" onChange={handleFileChange} />
            {uploadError && <p className="text-sm text-destructive mt-1">{uploadError}</p>}
          </div>
          
          {uploadProgress !== null && (
            <div className="w-full bg-secondary h-2 rounded-full overflow-hidden">
              <div 
                className="bg-primary h-full transition-all duration-300 ease-out" 
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          )}
          
          <div className="grid gap-2">
            <Label htmlFor="company">Linked Company (Optional)</Label>
            <Select value={companyId} onValueChange={setCompanyId}>
              <SelectTrigger>
                <SelectValue placeholder="Select a company" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">-- None --</SelectItem>
                {companies?.map(c => (
                  <SelectItem key={c.id} value={c.id.toString()}>{c.ticker} - {c.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div className="grid gap-2">
            <Label htmlFor="notes">Notes (Optional)</Label>
            <Textarea 
              id="notes" 
              placeholder="e.g. Sent via courier on May 5th"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </div>
        </div>
        
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={handleUpload} disabled={!file || uploadDoc.isPending}>
            {uploadDoc.isPending ? `Uploading... ${uploadProgress !== null ? uploadProgress + '%' : ''}` : "Upload"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
