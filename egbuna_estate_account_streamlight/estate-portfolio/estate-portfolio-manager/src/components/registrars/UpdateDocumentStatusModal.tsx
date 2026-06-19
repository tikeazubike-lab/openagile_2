import { useState, useEffect } from "react";
import { useUpdateDocumentStatus } from "@/api/queries";
import { useUIStore } from "@/store/uiStore";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";

interface Props {
  docId: number;
  currentStatus: string;
  isOpen: boolean;
  onClose: () => void;
}

export function UpdateDocumentStatusModal({ docId, currentStatus, isOpen, onClose }: Props) {
  const updateStatus = useUpdateDocumentStatus();
  const addToast = useUIStore((s) => s.addToast);
  
  const [status, setStatus] = useState(currentStatus);
  const [notes, setNotes] = useState("");

  useEffect(() => {
    if (isOpen) {
      setStatus(currentStatus || "pending");
      setNotes("");
    }
  }, [isOpen, currentStatus]);

  const handleSave = () => {
    updateStatus.mutate(
      { docId, status, notes: notes || undefined },
      {
        onSuccess: () => {
          addToast({ title: "Status updated", type: "success" });
          onClose();
        },
        onError: (err) => {
          addToast({ title: "Failed to update", description: err.message, type: "error" });
        }
      }
    );
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Update Document Status</DialogTitle>
        </DialogHeader>
        
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="status">Status</Label>
            <Select value={status} onValueChange={setStatus}>
              <SelectTrigger>
                <SelectValue placeholder="Select status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="submitted">Submitted</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="rejected">Rejected</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="grid gap-2">
            <Label htmlFor="notes">Status Notes (Optional)</Label>
            <Textarea 
              id="notes" 
              placeholder="e.g. Awaiting original copy"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </div>
        </div>
        
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={handleSave} disabled={updateStatus.isPending}>
            {updateStatus.isPending ? "Updating..." : "Update Status"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
