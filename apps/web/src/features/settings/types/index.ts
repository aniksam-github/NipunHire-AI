/**
 * Settings & Candidate Profile feature types.
 */

export interface EducationItem {
  institution: string;
  degree: string;
  field_of_study?: string;
  start_year?: number;
  end_year?: number;
}

export interface ExperienceItem {
  company: string;
  role: string;
  description?: string;
  start_date?: string;
  end_date?: string;
}

export interface ProjectItem {
  title: string;
  description?: string;
  url?: string;
}

export interface ProfileUpdate {
  headline?: string;
  bio?: string;
  education?: EducationItem[];
  experience?: ExperienceItem[];
  projects?: ProjectItem[];
  skills?: string[];
  certifications?: string[];
  github_username?: string;
  linkedin_url?: string;
  portfolio_url?: string;
}

export interface ProfileResponse {
  id: string;
  candidate_id: string;
  headline: string;
  bio: string;
  education: EducationItem[];
  experience: ExperienceItem[];
  projects: ProjectItem[];
  skills: string[];
  certifications: string[];
  github_username?: string;
  linkedin_url?: string;
  portfolio_url?: string;
  completion_percentage: number;
}
