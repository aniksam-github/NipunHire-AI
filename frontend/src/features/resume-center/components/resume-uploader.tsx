/**
 * ResumeUploader — drag and drop PDF uploader with PyMuPDF parsing status.
 */

import { useState, useRef } from "react";
import { Link } from "react-router-dom";
import { UploadCloud, Loader2, Sparkles, CheckCircle2 } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { useUploadResume as useUploadResumeHook } from "../hooks/use-resumes";

interface ResumeUploaderProps {
  onSuccess?: () => void;
}

export function ResumeUploader({ onSuccess }: ResumeUploaderProps) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [processingAcknowledged, setProcessingAcknowledged] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const uploadMutation = useUploadResumeHook();

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
      }
    }
  };

  const validateFile = (file: File): boolean => {
    if (!file.name.toLowerCase().endsWith(".pdf") && file.type !== "application/pdf") {
      alert("Please select a valid PDF file (.pdf).");
      return false;
    }
    if (file.size > 5 * 1024 * 1024) {
      alert("File size exceeds the 5 MB limit.");
      return false;
    }
    return true;
  };

  const handleUpload = () => {
    if (!selectedFile) return;
    uploadMutation.mutate(selectedFile, {
      onSuccess: () => {
        setSelectedFile(null);
        setProcessingAcknowledged(false);
        onSuccess?.();
      },
    });
  };

  return (
    <div className="glass-card p-6 rounded-2xl border border-border shadow-xl space-y-4">
      <div className="flex items-center gap-3">
        <div className="p-2.5 rounded-xl bg-fuchsia-600/20 text-fuchsia-400 border border-fuchsia-500/30">
          <Sparkles className="size-5" />
        </div>
        <div>
          <h3 className="text-lg font-extrabold text-foreground">Upload Resume for AI Parsing</h3>
          <p className="text-xs font-semibold text-foreground/80">
            PyMuPDF text extraction & ATS score analysis engine
          </p>
        </div>
      </div>

      <div className="rounded-xl border border-fuchsia-500/30 bg-fuchsia-500/10 p-3">
        <label htmlFor="ai-processing-acknowledged" className="flex cursor-pointer items-start gap-2.5 text-xs leading-5 text-foreground">
          <input
            id="ai-processing-acknowledged"
            type="checkbox"
            checked={processingAcknowledged}
            onChange={(event) => setProcessingAcknowledged(event.target.checked)}
            className="mt-0.5 size-4 accent-fuchsia-600"
          />
          <span>
            I understand that my resume and personal information will be processed by AI/LLM services, including the OpenAI API, for resume screening. See the{" "}
            <Link to="/privacy-policy" target="_blank" rel="noreferrer" className="font-semibold text-fuchsia-400 underline">Privacy Policy</Link>.
          </span>
        </label>
      </div>

      {/* Drag and Drop Zone */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all flex flex-col items-center justify-center space-y-3 ${
          dragActive
            ? "border-fuchsia-500 bg-fuchsia-500/10"
            : "border-border/80 hover:border-fuchsia-500/60 bg-background/50"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={handleFileChange}
        />

        <div className="size-12 rounded-2xl bg-fuchsia-600/15 text-fuchsia-400 flex items-center justify-center border border-fuchsia-500/20 shadow-md">
          <UploadCloud className="size-6" />
        </div>

        <div className="space-y-1">
          <p className="text-sm font-bold text-foreground">
            {selectedFile ? selectedFile.name : "Click to select or drag & drop your PDF resume"}
          </p>
          <p className="text-xs font-semibold text-foreground/70">
            Supports PDF files up to 5 MB
          </p>
        </div>

        {selectedFile && (
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 text-xs font-bold">
            <CheckCircle2 className="size-3.5" />
            <span>{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • Ready for AI Parsing</span>
          </div>
        )}
      </div>

      {/* Action Submit */}
      {selectedFile && (
        <div className="flex justify-end gap-3 pt-2">
          <Button
            variant="outline"
            onClick={() => setSelectedFile(null)}
            className="rounded-xl border-border text-foreground font-bold"
          >
            Cancel
          </Button>
          <Button
            onClick={handleUpload}
            disabled={uploadMutation.isPending || !processingAcknowledged}
            className="rounded-xl bg-fuchsia-600 hover:bg-fuchsia-700 text-white font-bold gap-2 shadow-md"
          >
            {uploadMutation.isPending ? (
              <>
                <Loader2 className="animate-spin size-4" />
                <span>Running PyMuPDF Parsing Engine...</span>
              </>
            ) : (
              <>
                <Sparkles className="size-4" />
                <span>Parse Resume & Calculate ATS Score</span>
              </>
            )}
          </Button>
        </div>
      )}
    </div>
  );
}
