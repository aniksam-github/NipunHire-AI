/**
 * Jobs feature types & Zod validation schemas.
 */

import { z } from "zod";

export type EmploymentType = "full_time" | "part_time" | "contract" | "internship";

export interface Job {
  id: string;
  title: string;
  description: string;
  department: string;
  location: string;
  employment_type: EmploymentType;
  min_experience_years: number;
  required_skills: string[];
  optional_skills: string[];
  is_active: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
}

// ---------------------------------------------------------------------------
// Zod Schema for Job Creation / Editing
// ---------------------------------------------------------------------------

export const jobFormSchema = z.object({
  title: z
    .string()
    .min(3, "Title must be at least 3 characters")
    .max(150, "Title must be under 150 characters"),
  description: z
    .string()
    .min(10, "Description must be at least 10 characters"),
  department: z
    .string()
    .min(1, "Department is required"),
  location: z
    .string()
    .min(1, "Location is required"),
  employment_type: z.enum(["full_time", "part_time", "contract", "internship"]),
  min_experience_years: z
    .number({ invalid_type_error: "Must be a number" })
    .min(0, "Experience cannot be negative"),
  required_skills: z
    .string()
    .min(1, "At least one required skill is recommended"),
  optional_skills: z.string(),
});

export type JobFormRawInput = z.infer<typeof jobFormSchema>;

export type JobCreatePayload = {
  title: string;
  description: string;
  department: string;
  location: string;
  employment_type: EmploymentType;
  min_experience_years: number;
  required_skills: string[];
  optional_skills: string[];
};
