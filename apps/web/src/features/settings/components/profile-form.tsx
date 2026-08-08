/**
 * ProfileForm — interactive form for updating candidate profile information, skills, and links.
 */

import { useState, useEffect } from "react";
import { Loader2, Save, UserCheck, Code, Globe, Link as LinkIcon } from "lucide-react";

import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import { useUpdateProfile } from "../hooks/use-settings";
import type { ProfileResponse } from "../types";

interface ProfileFormProps {
  profile: ProfileResponse;
}

export function ProfileForm({ profile }: ProfileFormProps) {
  const updateMutation = useUpdateProfile();

  const [headline, setHeadline] = useState(profile.headline || "");
  const [bio, setBio] = useState(profile.bio || "");
  const [skillsText, setSkillsText] = useState((profile.skills || []).join(", "));
  const [githubUsername, setGithubUsername] = useState(profile.github_username || "");
  const [linkedinUrl, setLinkedinUrl] = useState(profile.linkedin_url || "");
  const [portfolioUrl, setPortfolioUrl] = useState(profile.portfolio_url || "");

  useEffect(() => {
    setHeadline(profile.headline || "");
    setBio(profile.bio || "");
    setSkillsText((profile.skills || []).join(", "));
    setGithubUsername(profile.github_username || "");
    setLinkedinUrl(profile.linkedin_url || "");
    setPortfolioUrl(profile.portfolio_url || "");
  }, [profile]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const parsedSkills = skillsText
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    updateMutation.mutate({
      headline,
      bio,
      skills: parsedSkills,
      github_username: githubUsername || undefined,
      linkedin_url: linkedinUrl || undefined,
      portfolio_url: portfolioUrl || undefined,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Professional Headline */}
      <div className="space-y-1.5">
        <Label htmlFor="headline" className="text-xs font-bold uppercase tracking-wider text-foreground flex items-center gap-1.5">
          <UserCheck className="size-4 text-fuchsia-400" />
          <span>Professional Headline</span>
        </Label>
        <Input
          id="headline"
          type="text"
          placeholder="e.g. Senior AI Full-Stack Engineer | FastAPI & React Specialist"
          value={headline}
          onChange={(e) => setHeadline(e.target.value)}
          className="h-10 bg-background border-border text-foreground font-medium rounded-xl text-sm"
        />
      </div>

      {/* Bio / Summary */}
      <div className="space-y-1.5">
        <Label htmlFor="bio" className="text-xs font-bold uppercase tracking-wider text-foreground">
          Professional Summary & Background
        </Label>
        <textarea
          id="bio"
          rows={4}
          placeholder="Summarize your engineering background, core domain expertise, and achievements..."
          value={bio}
          onChange={(e) => setBio(e.target.value)}
          className="w-full p-3 rounded-xl bg-background border border-border text-foreground text-sm font-medium focus:border-fuchsia-500 focus:ring-2 focus:ring-fuchsia-500/30 outline-none resize-none"
        />
      </div>

      {/* Primary Technical Skills */}
      <div className="space-y-1.5">
        <Label htmlFor="skills" className="text-xs font-bold uppercase tracking-wider text-foreground flex items-center gap-1.5">
          <Code className="size-4 text-fuchsia-400" />
          <span>Primary Technical Skills (Comma Separated)</span>
        </Label>
        <Input
          id="skills"
          type="text"
          placeholder="FastAPI, React, TypeScript, MongoDB, PyMuPDF, Docker, Python"
          value={skillsText}
          onChange={(e) => setSkillsText(e.target.value)}
          className="h-10 bg-background border-border text-foreground font-medium rounded-xl text-sm"
        />
        <p className="text-[11px] font-semibold text-foreground/70">
          These skills feed directly into the Gemini ATS candidate matching engine.
        </p>
      </div>

      {/* External Links Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
        {/* GitHub */}
        <div className="space-y-1.5">
          <Label htmlFor="github" className="text-xs font-bold uppercase tracking-wider text-foreground flex items-center gap-1.5">
            <LinkIcon className="size-4 text-fuchsia-400" />
            <span>GitHub Username</span>
          </Label>
          <Input
            id="github"
            type="text"
            placeholder="e.g. aniketsamanta"
            value={githubUsername}
            onChange={(e) => setGithubUsername(e.target.value)}
            className="h-10 bg-background border-border text-foreground font-medium rounded-xl text-xs"
          />
        </div>

        {/* LinkedIn */}
        <div className="space-y-1.5">
          <Label htmlFor="linkedin" className="text-xs font-bold uppercase tracking-wider text-foreground flex items-center gap-1.5">
            <Globe className="size-4 text-fuchsia-400" />
            <span>LinkedIn URL</span>
          </Label>
          <Input
            id="linkedin"
            type="url"
            placeholder="https://linkedin.com/in/..."
            value={linkedinUrl}
            onChange={(e) => setLinkedinUrl(e.target.value)}
            className="h-10 bg-background border-border text-foreground font-medium rounded-xl text-xs"
          />
        </div>

        {/* Portfolio */}
        <div className="space-y-1.5">
          <Label htmlFor="portfolio" className="text-xs font-bold uppercase tracking-wider text-foreground flex items-center gap-1.5">
            <Globe className="size-4 text-fuchsia-400" />
            <span>Portfolio Website</span>
          </Label>
          <Input
            id="portfolio"
            type="url"
            placeholder="https://yourportfolio.dev"
            value={portfolioUrl}
            onChange={(e) => setPortfolioUrl(e.target.value)}
            className="h-10 bg-background border-border text-foreground font-medium rounded-xl text-xs"
          />
        </div>
      </div>

      {/* Action Submit */}
      <div className="flex justify-end pt-4 border-t border-border">
        <Button
          type="submit"
          disabled={updateMutation.isPending}
          className="rounded-xl bg-fuchsia-600 hover:bg-fuchsia-700 text-white font-bold text-xs gap-2 shadow-md px-6 h-10"
        >
          {updateMutation.isPending ? (
            <>
              <Loader2 className="animate-spin size-4" />
              <span>Saving Profile...</span>
            </>
          ) : (
            <>
              <Save className="size-4" />
              <span>Save Profile Changes</span>
            </>
          )}
        </Button>
      </div>
    </form>
  );
}
