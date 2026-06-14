import { useState, useEffect } from "react";
import { useAddRequirement, useUpdateRequirement } from "@/api/queries";
import { useUIStore } from "@/store/uiStore";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";

const COMMON_TASKS = [
  "Unclaimed Dividend Claim",
  "Dematerialisation",
  "Share Certificate Digitisation",
  "KYC Update",
  "Account Reactivation",
  "Delisted Company Claim"
];

interface Props {
  registrarId: number;
  isOpen: boolean;
  onClose: () => void;
  existingReq?: any;
}

export function AddRequirementModal({ registrarId, isOpen, onClose, existingReq }: Props) {
  const addReq = useAddRequirement();
  const updateReq = useUpdateRequirement();
  const addToast = useUIStore((s) => s.addToast);
  
  const [taskName, setTaskName] = useState<string>("");
  const [customTask, setCustomTask] = useState("");
  const [docTitle, setDocTitle] = useState("");
  const [description, setDescription] = useState("");
  const [isRequired, setIsRequired] = useState(true);

  useEffect(() => {
    if (existingReq && isOpen) {
      if (COMMON_TASKS.includes(existingReq.task_name)) {
        setTaskName(existingReq.task_name);
        setCustomTask("");
      } else {
        setTaskName("Other");
        setCustomTask(existingReq.task_name);
      }
      setDocTitle(existingReq.document_title || "");
      setDescription(existingReq.description || "");
      setIsRequired(existingReq.is_required !== false);
    } else if (isOpen) {
      setTaskName("");
      setCustomTask("");
      setDocTitle("");
      setDescription("");
      setIsRequired(true);
    }
  }, [existingReq, isOpen]);

  const handleSave = () => {
    const finalTaskName = taskName === "Other" ? customTask : taskName;
    if (!finalTaskName || !docTitle) {
      addToast({ title: "Missing fields", description: "Task Name and Document Title are required.", type: "error" });
      return;
    }

    const payload = {
      registrarId,
      task_name: finalTaskName,
      document_title: docTitle,
      description: description || undefined,
      is_required: isRequired,
      sort_order: existingReq ? existingReq.sort_order : 0,
    };

    if (existingReq) {
      updateReq.mutate(
        { id: existingReq.id, ...payload },
        {
          onSuccess: () => {
            addToast({ title: "Requirement updated", type: "success" });
            onClose();
          },
          onError: (err) => {
            addToast({ title: "Failed to update", description: err.message, type: "error" });
          }
        }
      );
    } else {
      addReq.mutate(
        payload,
        {
          onSuccess: () => {
            addToast({ title: "Requirement added", type: "success" });
            onClose();
          },
          onError: (err) => {
            addToast({ title: "Failed to add", description: err.message, type: "error" });
          }
        }
      );
    }
  };

  const isPending = addReq.isPending || updateReq.isPending;

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{existingReq ? "Edit Requirement" : "Add Requirement"}</DialogTitle>
        </DialogHeader>
        
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="task">Task Name</Label>
            <Select value={taskName} onValueChange={setTaskName}>
              <SelectTrigger>
                <SelectValue placeholder="Select a task category" />
              </SelectTrigger>
              <SelectContent>
                {COMMON_TASKS.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                <SelectItem value="Other">Other (Custom)</SelectItem>
              </SelectContent>
            </Select>
            {taskName === "Other" && (
              <Input 
                placeholder="Enter custom task name" 
                value={customTask} 
                onChange={(e) => setCustomTask(e.target.value)} 
                className="mt-2"
              />
            )}
          </div>
          
          <div className="grid gap-2">
            <Label htmlFor="docTitle">Document Title</Label>
            <Input 
              id="docTitle" 
              placeholder="e.g. Proof of Identity"
              value={docTitle}
              onChange={(e) => setDocTitle(e.target.value)}
            />
          </div>
          
          <div className="grid gap-2">
            <Label htmlFor="description">Description (Optional)</Label>
            <Textarea 
              id="description" 
              placeholder="e.g. Copy of NIN Slip or Intl Passport"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          
          <div className="flex items-center space-x-2 mt-2">
            <Switch 
              id="required" 
              checked={isRequired}
              onCheckedChange={setIsRequired}
            />
            <Label htmlFor="required">Required Document</Label>
          </div>
        </div>
        
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={handleSave} disabled={isPending}>
            {isPending ? "Saving..." : "Save Requirement"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
