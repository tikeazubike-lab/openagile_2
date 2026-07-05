import { useState, useMemo } from "react";
import { useRegistrarRequirements, useDeleteDocument, useDeleteRequirement, useUpdateDocumentStatus } from "@/api/queries";
import { useAuthStore } from "@/store/authStore";
import { useUIStore } from "@/store/uiStore";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, ChevronDown, ChevronRight, FileUp, Download, Trash2, Clock, CheckCircle2, AlertCircle, FileText, Edit } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { DocumentUploadModal } from "./DocumentUploadModal";
import { DocumentHistoryModal } from "./DocumentHistoryModal";
import { AddRequirementModal } from "./AddRequirementModal";
import { cn } from "@/lib/utils";

export function RegistrarRequirements({ registrarId }: { registrarId: number }) {
  const { data: requirements, isLoading } = useRegistrarRequirements(registrarId);
  const isAdmin = useAuthStore((s) => s.isAdmin)();
  const deleteDocument = useDeleteDocument();
  const deleteRequirement = useDeleteRequirement();
  const updateStatusMutation = useUpdateDocumentStatus();
  
  const [expandedTasks, setExpandedTasks] = useState<Record<string, boolean>>({});
  const [uploadReqId, setUploadReqId] = useState<number | null>(null);
  const [historyReqId, setHistoryReqId] = useState<number | null>(null);
  const [isAddReqOpen, setIsAddReqOpen] = useState(false);
  const [editReqData, setEditReqData] = useState<any | null>(null);

  const handleDownload = async (docId: number, fileName: string) => {
    try {
      const response = await fetch(`/api/v1/registrar-documents/${docId}/download`, {
        credentials: 'include',
      });
      if (!response.ok) throw new Error('Download failed');
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      useUIStore.getState().addToast({ title: "Download failed", description: "Please log in again", type: "error" });
    }
  };

  const toggleTask = (taskName: string) => {
    setExpandedTasks(prev => ({ ...prev, [taskName]: !prev[taskName] }));
  };

  const groupedRequirements = useMemo(() => {
    if (!requirements) return {};
    return requirements.reduce((acc: any, req: any) => {
      if (!acc[req.task_name]) acc[req.task_name] = [];
      acc[req.task_name].push(req);
      return acc;
    }, {});
  }, [requirements]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <Badge className="bg-green-100 text-green-700 hover:bg-green-100 border-none"><CheckCircle2 className="mr-1 h-3 w-3" /> Completed</Badge>;
      case "submitted":
        return <Badge className="bg-blue-100 text-blue-700 hover:bg-blue-100 border-none"><Clock className="mr-1 h-3 w-3" /> Submitted</Badge>;
      case "rejected":
        return <Badge className="bg-red-100 text-red-700 hover:bg-red-100 border-none"><AlertCircle className="mr-1 h-3 w-3" /> Rejected</Badge>;
      case "pending":
      default:
        return <Badge className="bg-amber-100 text-amber-700 hover:bg-amber-100 border-none"><Clock className="mr-1 h-3 w-3" /> Pending</Badge>;
    }
  };

  if (isLoading) return <div className="text-center py-4">Loading requirements...</div>;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <CardTitle className="text-lg">Requirements & Documents</CardTitle>
        {isAdmin && (
          <Button size="sm" onClick={() => setIsAddReqOpen(true)}>
            <Plus className="mr-2 h-4 w-4" /> Add Requirement
          </Button>
        )}
      </CardHeader>
      <CardContent className="p-0">
        <div className="flex flex-col divide-y">
          {Object.entries(groupedRequirements).map(([taskName, reqs]: [string, any]) => (
            <div key={taskName} className="flex flex-col">
              <div className="flex items-center justify-between bg-muted/30 px-6 py-3 font-semibold hover:bg-muted/50 transition-colors">
                <button
                  className="flex flex-1 items-center gap-2 text-sm text-left"
                  onClick={() => toggleTask(taskName)}
                >
                  {expandedTasks[taskName] ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                  {taskName.toUpperCase()}
                </button>
                <div className="flex items-center gap-3">
                  <Badge variant="outline">{reqs.length} items</Badge>
                  {isAdmin && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (confirm(`This will delete all ${reqs.length} requirements in this group and their associated documents. Are you sure?`)) {
                          reqs.forEach((r: any) => deleteRequirement.mutate(r.id));
                        }
                      }}
                      className="text-[var(--accent-red)] text-destructive hover:opacity-80"
                      title="Delete this requirement group"
                    >
                      <Trash2 size={14} />
                    </button>
                  )}
                </div>
              </div>
              
              {expandedTasks[taskName] && (
                <div className="flex flex-col bg-card">
                  {/* Table Header */}
                  <div className="grid grid-cols-12 gap-4 px-6 py-2 text-xs font-medium text-muted-foreground border-b bg-muted/10">
                    <div className="col-span-4">Document</div>
                    <div className="col-span-2">Status</div>
                    <div className="col-span-4">File</div>
                    <div className="col-span-2 text-right">Action</div>
                  </div>
                  
                  {/* Rows */}
                  {reqs.map((req: any) => (
                    <div key={req.id} className="grid grid-cols-12 gap-4 px-6 py-3 items-center text-sm border-b last:border-0 hover:bg-muted/5 transition-colors group">
                      <div className="col-span-4 flex flex-col">
                        <span className="font-medium flex items-center gap-2">
                          {req.document_title}
                          {req.is_required && <span className="text-red-500 text-xs font-bold" title="Required">*</span>}
                          {isAdmin && (
                            <div className="opacity-0 group-hover:opacity-100 flex items-center gap-1 transition-opacity ml-1">
                              <button onClick={() => setEditReqData(req)} className="p-1 text-muted-foreground hover:text-primary hover:bg-muted rounded">
                                <Edit className="h-3.5 w-3.5" />
                              </button>
                              <button 
                                onClick={() => {
                                  if (confirm("Are you sure you want to delete this requirement? All associated documents will also be removed.")) {
                                    deleteRequirement.mutate(req.id);
                                  }
                                }} 
                                className="p-1 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded"
                              >
                                <Trash2 className="h-3.5 w-3.5" />
                              </button>
                            </div>
                          )}
                        </span>
                        {req.description && <span className="text-xs text-muted-foreground truncate">{req.description}</span>}
                      </div>
                      
                      <div className="col-span-2 flex items-center gap-1 group/status">
                        {!req.latest_document ? (
                          <Badge variant="outline" className="text-muted-foreground border-dashed">Missing</Badge>
                        ) : isAdmin ? (
                          <select
                            className="text-xs bg-background border rounded px-1 py-0.5 h-7 w-full"
                            value={req.latest_document.status}
                            onChange={(e) => updateStatusMutation.mutate({
                              docId: req.latest_document.id,
                              status: e.target.value
                            })}
                          >
                            <option value="pending">Pending</option>
                            <option value="submitted">Submitted to registrar</option>
                            <option value="completed">Completed</option>
                            <option value="rejected">Rejected - re-upload needed</option>
                          </select>
                        ) : (
                          getStatusBadge(req.latest_document.status)
                        )}
                      </div>
                      
                      <div className="col-span-4 flex flex-col items-start justify-center">
                        {req.latest_document ? (
                          <div className="flex flex-col items-start gap-1">
                            <div className="flex items-center gap-1.5 text-xs font-medium">
                              <FileText className="h-3.5 w-3.5 text-muted-foreground" />
                              <span className="truncate max-w-[150px]" title={req.latest_document.file_name}>
                                {req.latest_document.file_name}
                              </span>
                              {req.latest_document.company_ticker && (
                                <Badge variant="secondary" className="text-[10px] px-1 py-0 h-4">
                                  {req.latest_document.company_ticker}
                                </Badge>
                              )}
                            </div>
                            {req.document_count > 1 && (
                              <button 
                                onClick={() => setHistoryReqId(req.id)}
                                className="text-[10px] text-primary hover:underline"
                              >
                                Show history ({req.document_count} versions)
                              </button>
                            )}
                          </div>
                        ) : (
                          <span className="text-muted-foreground text-xs italic">—</span>
                        )}
                      </div>
                      
                      <div className="col-span-2 flex items-center justify-end gap-2">
                        {req.latest_document ? (
                          <>
                            {isAdmin && (
                              <Button 
                                variant="ghost" 
                                size="icon" 
                                className="h-7 w-7 text-primary hover:text-primary hover:bg-primary/10"
                                onClick={() => setUploadReqId(req.id)}
                                title="Upload New Version"
                              >
                                <FileUp className="h-3.5 w-3.5" />
                              </Button>
                            )}
                            <Button 
                              variant="ghost" 
                              size="icon" 
                              className="h-7 w-7"
                              onClick={() => handleDownload(req.latest_document.id, req.latest_document.file_name)}
                              title="Download Latest"
                            >
                              <Download className="h-3.5 w-3.5" />
                            </Button>
                            {isAdmin && (
                              <Button 
                                variant="ghost" 
                                size="icon" 
                                className="h-7 w-7 text-destructive hover:text-destructive hover:bg-destructive/10"
                                onClick={() => deleteDocument.mutate(req.latest_document.id)}
                                title="Delete Latest"
                              >
                                <Trash2 className="h-3.5 w-3.5" />
                              </Button>
                            )}
                          </>
                        ) : (
                          isAdmin && (
                            <Button 
                              variant="outline" 
                              size="sm" 
                              className="h-7 px-2 text-xs"
                              onClick={() => setUploadReqId(req.id)}
                            >
                              <FileUp className="h-3 w-3 mr-1" /> Upload
                            </Button>
                          )
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
          {Object.keys(groupedRequirements).length === 0 && (
            <div className="p-8 text-center text-muted-foreground">
              No requirements configured for this registrar.
            </div>
          )}
        </div>
      </CardContent>

      {uploadReqId && (
        <DocumentUploadModal 
          reqId={uploadReqId} 
          isOpen={!!uploadReqId} 
          onClose={() => setUploadReqId(null)} 
        />
      )}
      
      {historyReqId && (
        <DocumentHistoryModal 
          reqId={historyReqId} 
          isOpen={!!historyReqId} 
          onClose={() => setHistoryReqId(null)} 
        />
      )}

      {isAddReqOpen && (
        <AddRequirementModal 
          registrarId={registrarId} 
          isOpen={isAddReqOpen} 
          onClose={() => setIsAddReqOpen(false)} 
        />
      )}

      {editReqData && (
        <AddRequirementModal 
          registrarId={registrarId} 
          isOpen={!!editReqData} 
          onClose={() => setEditReqData(null)} 
          existingReq={editReqData}
        />
      )}
    </Card>
  );
}
