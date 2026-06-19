import { useDocumentHistory } from "@/api/queries";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";

interface Props {
  reqId: number;
  isOpen: boolean;
  onClose: () => void;
}

export function DocumentHistoryModal({ reqId, isOpen, onClose }: Props) {
  const { data: history, isLoading } = useDocumentHistory(reqId);

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>Document History</DialogTitle>
        </DialogHeader>
        
        <div className="py-4">
          {isLoading ? (
            <div className="text-center">Loading history...</div>
          ) : (
            <div className="flex flex-col border rounded-md divide-y">
              <div className="grid grid-cols-12 gap-4 px-4 py-2 bg-muted/30 text-xs font-semibold">
                <div className="col-span-2">Version</div>
                <div className="col-span-3">Date</div>
                <div className="col-span-2">Size</div>
                <div className="col-span-2">Status</div>
                <div className="col-span-2">Uploaded By</div>
                <div className="col-span-1 text-right">Dl</div>
              </div>
              
              {history?.map((doc) => (
                <div key={doc.id} className={`grid grid-cols-12 gap-4 px-4 py-2 items-center text-sm ${doc.is_deleted ? 'opacity-50 line-through' : ''}`}>
                  <div className="col-span-2 font-medium">{doc.version}</div>
                  <div className="col-span-3">{new Date(doc.uploaded_at).toLocaleString()}</div>
                  <div className="col-span-2">{(doc.file_size / 1024 / 1024).toFixed(2)} MB</div>
                  <div className="col-span-2 capitalize">{doc.status}</div>
                  <div className="col-span-2 truncate">{doc.uploaded_by_name}</div>
                  <div className="col-span-1 text-right">
                    {!doc.is_deleted && (
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        className="h-6 w-6"
                        onClick={() => window.location.href = `/api/v1/registrar-documents/${doc.id}/download`}
                      >
                        <Download className="h-3 w-3" />
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
