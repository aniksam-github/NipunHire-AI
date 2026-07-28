/**
 * ResumeCenterPage — main view for uploading, managing versions, and viewing ATS analysis.
 */

import { useState } from "react";
import { FileText, History, Trash2, Loader2 } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { ATSBadge } from "@/shared/design-system";
import { ResumeUploader } from "./resume-uploader";
import { ResumeAnalysis } from "./resume-analysis";
import { useResumesList, useDeleteResume } from "../hooks/use-resumes";

export function ResumeCenterPage() {
  const { data: resumes = [], isLoading } = useResumesList();
  const deleteMutation = useDeleteResume();

  const [selectedResumeId, setSelectedResumeId] = useState<string | null>(null);

  const activeResume = resumes.find((r) => r.id === selectedResumeId) ?? resumes[0];

  const handleDelete = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (confirm("Delete this resume version?")) {
      deleteMutation.mutate(id);
      if (selectedResumeId === id) {
        setSelectedResumeId(null);
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-card p-6 rounded-2xl border border-border shadow-xl">
        <div className="space-y-1">
          <h2 className="text-2xl font-extrabold tracking-tight text-foreground flex items-center gap-2">
            <span>Resume Center</span>
            <FileText className="size-5 text-fuchsia-400" />
          </h2>
          <p className="text-xs font-semibold text-foreground/80">
            Upload PDF resumes for PyMuPDF parsing, ATS Health scoring, and skill extraction.
          </p>
        </div>
      </div>

      {/* Upload Section */}
      <ResumeUploader />

      {/* Loading State */}
      {isLoading && (
        <div className="flex flex-col items-center justify-center p-12 space-y-3 glass-card rounded-2xl border border-border">
          <Loader2 className="animate-spin size-8 text-fuchsia-400" />
          <p className="text-xs font-bold text-foreground">Fetching uploaded resumes...</p>
        </div>
      )}

      {/* Resume Version History & Active Analysis */}
      {!isLoading && resumes.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* History Sidebar */}
          <div className="glass-card p-5 rounded-2xl border border-border space-y-3 h-fit">
            <h3 className="text-sm font-extrabold text-foreground flex items-center gap-2 border-b border-border pb-3">
              <History className="size-4 text-fuchsia-400" />
              <span>Resume Versions ({resumes.length})</span>
            </h3>

            <div className="space-y-2">
              {resumes.map((item) => {
                const isSelected = item.id === activeResume?.id;
                return (
                  <div
                    key={item.id}
                    onClick={() => setSelectedResumeId(item.id)}
                    className={`p-3 rounded-xl border text-xs font-semibold cursor-pointer transition-all space-y-1.5 ${
                      isSelected
                        ? "bg-fuchsia-600/20 border-fuchsia-500/50 shadow-sm"
                        : "bg-background/60 border-border/60 hover:bg-accent"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-foreground truncate max-w-[120px]">
                        {item.filename}
                      </span>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={(e) => handleDelete(e, item.id)}
                        className="size-6 text-muted-foreground hover:text-destructive"
                      >
                        <Trash2 className="size-3" />
                      </Button>
                    </div>
                    <div className="flex items-center justify-between text-[10px] font-bold">
                      <span className="text-foreground/70">
                        {new Date(item.created_at).toLocaleDateString()}
                      </span>
                      <ATSBadge score={item.ats_score} showIcon={false} className="text-[10px] px-1.5 py-0.5" />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Active Scorecard Display */}
          <div className="lg:col-span-3">
            {activeResume && <ResumeAnalysis resume={activeResume} />}
          </div>
        </div>
      )}
    </div>
  );
}
