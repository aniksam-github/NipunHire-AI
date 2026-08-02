/**
 * ResumeAnalysis — detailed ATS Resume Health Scorecard & AI Quality Feedback view.
 * Includes persistent AI correction paths via PATCH API (#5), human-in-the-loop trust badges (#11),
 * and guided next steps (#13).
 */

import { useState } from "react";
import {
  CheckCircle2,
  AlertTriangle,
  Lightbulb,
  Mail,
  Phone,
  Cpu,
  FileCheck,
  Edit3,
  Check,
  Plus,
  X,
  Bot,
  Loader2,
} from "lucide-react";
import {
  ATSBadge,
  SkillTag,
  ConfidenceMeter,
  HumanDecisionTrustBadge,
  GuidedNextStepCard,
} from "@/shared/design-system";
import { Button } from "@/shared/components/ui/button";
import { updateResumeParsedData } from "../api/resumes-api";
import type { Resume } from "../types";

interface ResumeAnalysisProps {
  resume: Resume;
  onUpdateResume?: (updated: Resume) => void;
}

export function ResumeAnalysis({ resume, onUpdateResume }: ResumeAnalysisProps) {
  const { quality_breakdown, ai_feedback } = resume;

  // Local & persisted state for AI correction path (Checklist #5)
  const [isEditingContact, setIsEditingContact] = useState(false);
  const [email, setEmail] = useState(resume.parsed_email ?? "");
  const [phone, setPhone] = useState(resume.parsed_phone ?? "");

  const [skills, setSkills] = useState<string[]>(resume.extracted_skills ?? []);
  const [newSkillInput, setNewSkillInput] = useState("");
  const [isAddingSkill, setIsAddingSkill] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [feedbackSaved, setFeedbackSaved] = useState(false);

  const persistCorrections = async (newEmail?: string, newPhone?: string, newSkills?: string[]) => {
    setIsSaving(true);
    try {
      const updated = await updateResumeParsedData(resume.id, {
        parsed_email: newEmail ?? email,
        parsed_phone: newPhone ?? phone,
        extracted_skills: newSkills ?? skills,
      });
      if (onUpdateResume) {
        onUpdateResume(updated);
      }
      setFeedbackSaved(true);
      setTimeout(() => setFeedbackSaved(false), 3000);
    } catch (err) {
      console.error("Failed to persist resume AI corrections", err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleSaveContact = async () => {
    setIsEditingContact(false);
    await persistCorrections(email, phone, skills);
  };

  const handleAddSkill = async () => {
    if (newSkillInput.trim() && !skills.includes(newSkillInput.trim())) {
      const updatedSkills = [...skills, newSkillInput.trim()];
      setSkills(updatedSkills);
      setNewSkillInput("");
      setIsAddingSkill(false);
      await persistCorrections(email, phone, updatedSkills);
    }
  };

  const handleRemoveSkill = async (skillToRemove: string) => {
    const updatedSkills = skills.filter((s) => s !== skillToRemove);
    setSkills(updatedSkills);
    await persistCorrections(email, phone, updatedSkills);
  };

  return (
    <div className="space-y-6">
      {/* Mandatory Human-in-the-Loop Trust Badge (Checklist #11) */}
      <HumanDecisionTrustBadge message="ATS compatibility and extracted skills are AI decision-support signals designed to accelerate resume screening. You can edit any mis-parsed fields below." />

      {/* ATS Overall Score Header Banner */}
      <div className="glass-card p-6 rounded-2xl border border-border shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-fuchsia-500/20 text-fuchsia-300 font-mono uppercase">
                {resume.filename}
              </span>
              <span className="text-xs font-semibold text-foreground/70">
                {resume.page_count} Page{resume.page_count > 1 ? "s" : ""} •{" "}
                {(resume.file_size_bytes / 1024).toFixed(1)} KB
              </span>
            </div>
            <h2 className="text-2xl font-extrabold tracking-tight text-foreground">
              ATS Resume Health Scorecard
            </h2>
          </div>
          <ATSBadge score={resume.ats_score} className="text-sm px-4 py-2" />
        </div>

        <ConfidenceMeter score={resume.ats_score} label="Overall ATS Compatibility Index" />
      </div>

      {/* Save Notification */}
      {feedbackSaved && (
        <div className="p-3 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-bold flex items-center gap-2 animate-fade-in">
          <Check className="size-4" />
          <span>Parsed details saved to database! AI evaluation matrix updated & persisted.</span>
        </div>
      )}

      {/* 3 Quality Sub-Scores Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="glass-card p-5 rounded-2xl border border-border space-y-2">
          <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
            Contact Completeness
          </span>
          <div className="text-2xl font-extrabold text-foreground">
            {quality_breakdown.completeness_score}%
          </div>
          <p className="text-xs font-semibold text-foreground/70">Email & Phone verification</p>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-border space-y-2">
          <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
            Keyword Density
          </span>
          <div className="text-2xl font-extrabold text-foreground">
            {quality_breakdown.keyword_density_score}%
          </div>
          <p className="text-xs font-semibold text-foreground/70">Extracted tech skills count</p>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-border space-y-2">
          <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
            Formatting & Structure
          </span>
          <div className="text-2xl font-extrabold text-foreground">
            {quality_breakdown.formatting_score}%
          </div>
          <p className="text-xs font-semibold text-foreground/70">Page count & text density</p>
        </div>
      </div>

      {/* Contact Info & Extracted Tech Skills Matrix with API Correction Persistence (#5) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Parsed Contact Info (Editable & Persistent) */}
        <div className="glass-card p-6 rounded-2xl border border-border space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-extrabold text-foreground flex items-center gap-2">
              <FileCheck className="size-4 text-fuchsia-400" />
              <span>Parsed Contact Attributes</span>
            </h3>
            <Button
              onClick={() => (isEditingContact ? handleSaveContact() : setIsEditingContact(true))}
              disabled={isSaving}
              variant="outline"
              className="h-8 text-xs font-bold px-3 gap-1.5 border-border"
            >
              {isSaving ? (
                <Loader2 className="size-3.5 animate-spin text-fuchsia-400" />
              ) : isEditingContact ? (
                <>
                  <Check className="size-3.5 text-emerald-400" /> Save Edits
                </>
              ) : (
                <>
                  <Edit3 className="size-3.5 text-fuchsia-400" /> Edit Contact
                </>
              )}
            </Button>
          </div>

          <div className="space-y-3 text-xs font-semibold">
            <div className="flex items-center gap-3 p-3 rounded-xl bg-background border border-border/60">
              <Mail className="size-4 text-fuchsia-400 shrink-0" />
              <div className="flex-1">
                <p className="text-foreground/70 text-[10px]">Extracted Email</p>
                {isEditingContact ? (
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-secondary px-2.5 py-1 rounded-lg border border-fuchsia-500/40 text-foreground font-bold focus:outline-none focus:ring-1 focus:ring-fuchsia-500"
                  />
                ) : (
                  <p className="text-foreground font-bold">{email || "Not Detected"}</p>
                )}
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 rounded-xl bg-background border border-border/60">
              <Phone className="size-4 text-fuchsia-400 shrink-0" />
              <div className="flex-1">
                <p className="text-foreground/70 text-[10px]">Extracted Phone</p>
                {isEditingContact ? (
                  <input
                    type="text"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="w-full bg-secondary px-2.5 py-1 rounded-lg border border-fuchsia-500/40 text-foreground font-bold focus:outline-none focus:ring-1 focus:ring-fuchsia-500"
                  />
                ) : (
                  <p className="text-foreground font-bold">{phone || "Not Detected"}</p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Extracted Skills Matrix (Editable & Persistent) */}
        <div className="glass-card p-6 rounded-2xl border border-border space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-extrabold text-foreground flex items-center gap-2">
              <Cpu className="size-4 text-fuchsia-400" />
              <span>Extracted Tech Skills ({skills.length})</span>
            </h3>
            <Button
              onClick={() => setIsAddingSkill(!isAddingSkill)}
              disabled={isSaving}
              variant="outline"
              className="h-8 text-xs font-bold px-3 gap-1 border-border"
            >
              <Plus className="size-3.5 text-fuchsia-400" /> Add Skill
            </Button>
          </div>

          {isAddingSkill && (
            <div className="flex items-center gap-2 p-2 rounded-xl bg-background border border-fuchsia-500/40">
              <input
                type="text"
                placeholder="Enter technical skill (e.g. Python, Docker)..."
                value={newSkillInput}
                onChange={(e) => setNewSkillInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAddSkill()}
                className="flex-1 bg-transparent px-2 text-xs font-bold text-foreground focus:outline-none"
              />
              <Button
                onClick={handleAddSkill}
                disabled={isSaving}
                className="h-7 px-3 text-[11px] font-bold bg-fuchsia-600 hover:bg-fuchsia-700 text-white rounded-lg"
              >
                {isSaving ? <Loader2 className="size-3 animate-spin" /> : "Add"}
              </Button>
            </div>
          )}

          <div className="flex flex-wrap gap-1.5 pt-1">
            {skills.length > 0 ? (
              skills.map((skill, i) => (
                <div key={i} className="inline-flex items-center gap-1">
                  <SkillTag name={skill} status="matched" />
                  <button
                    onClick={() => handleRemoveSkill(skill)}
                    disabled={isSaving}
                    className="p-0.5 rounded-full hover:bg-destructive/20 text-muted-foreground hover:text-destructive transition-colors disabled:opacity-50"
                    title="Remove skill"
                  >
                    <X className="size-3" />
                  </button>
                </div>
              ))
            ) : (
              <p className="text-xs font-semibold text-foreground/70">
                No standard tech skills detected in text. Click 'Add Skill' to insert.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* AI Suggestions & Improvements Box */}
      <div className="glass-card p-6 rounded-2xl border border-border space-y-4">
        <h3 className="text-base font-extrabold text-foreground flex items-center gap-2">
          <Lightbulb className="size-5 text-amber-400" />
          <span>AI Resume Quality Recommendations</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-semibold">
          <div className="p-4 rounded-xl bg-background border border-border/60 space-y-2">
            <p className="font-bold text-foreground flex items-center gap-1.5">
              <AlertTriangle className="size-4 text-amber-400" />
              <span>Missing & Recommended Keywords</span>
            </p>
            <ul className="space-y-1 text-foreground/80 list-disc list-inside">
              {ai_feedback.missing_elements.length > 0 ? (
                ai_feedback.missing_elements.map((item, i) => <li key={i}>{item}</li>)
              ) : (
                <li>No critical elements missing! Great job.</li>
              )}
            </ul>
          </div>

          <div className="p-4 rounded-xl bg-background border border-border/60 space-y-2">
            <p className="font-bold text-foreground flex items-center gap-1.5">
              <CheckCircle2 className="size-4 text-emerald-400" />
              <span>High-Impact Action Verbs to Include</span>
            </p>
            <div className="flex flex-wrap gap-1.5 pt-1">
              {ai_feedback.action_verb_suggestions.map((verb, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-300 text-[11px] font-bold"
                >
                  {verb}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Guided Next-Step Card with Easy Exit (Rule #3, #4 & Checklist Item #13) */}
      <GuidedNextStepCard
        title="Ready to test your resume in an AI Practice Session?"
        description="Launch an adaptive multi-turn AI interview based on your parsed skills, or check job compatibility scores."
        actionLabel="Start AI Mock Interview"
        actionPath="/interviews"
        icon={<Bot className="size-5 text-fuchsia-400" />}
      />
    </div>
  );
}
