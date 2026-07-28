/**
 * JobList — main view for listing & managing job positions.
 */

import { useState } from "react";
import { Plus, Search, Filter, Briefcase, Sparkles, Loader2 } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { JobCard } from "./job-card";
import { JobCreateModal } from "./job-create-modal";
import { useJobsList } from "../hooks/use-jobs";
import { useAuthStore } from "@/features/auth/stores/auth-store";

export function JobList() {
  const user = useAuthStore((s) => s.user);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterDepartment, setFilterDepartment] = useState("all");

  const { data: jobs = [], isLoading } = useJobsList();

  const isRecruiter = user?.role === "recruiter" || user?.role === "admin";

  const filteredJobs = jobs.filter((job) => {
    const matchesSearch =
      job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.location.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDept = filterDepartment === "all" || job.department === filterDepartment;
    return matchesSearch && matchesDept;
  });

  const departments = Array.from(new Set(jobs.map((j) => j.department)));

  return (
    <div className="space-y-6">
      {/* Page Banner & Action Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-card p-6 rounded-2xl border border-border shadow-xl">
        <div className="space-y-1">
          <h2 className="text-2xl font-extrabold tracking-tight text-foreground flex items-center gap-2">
            <span>Job Positions</span>
            <Briefcase className="size-5 text-fuchsia-400" />
          </h2>
          <p className="text-xs font-semibold text-foreground/80">
            Manage open roles, define required skill weights, and run candidate screenings.
          </p>
        </div>

        {isRecruiter && (
          <Button
            onClick={() => setIsModalOpen(true)}
            className="h-11 rounded-xl bg-fuchsia-600 hover:bg-fuchsia-700 text-white font-bold text-xs shadow-md gap-2"
          >
            <Plus className="size-4" />
            <span>Post New Job Position</span>
          </Button>
        )}
      </div>

      {/* Filter & Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-card/60 p-4 rounded-2xl border border-border/80">
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 size-4 text-fuchsia-400" />
          <Input
            type="text"
            placeholder="Search by title, location..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 h-10 bg-background border-border text-foreground text-xs font-medium placeholder:text-muted-foreground/90 rounded-xl"
          />
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          <div className="flex items-center gap-2 text-xs font-bold text-foreground/80">
            <Filter className="size-4 text-fuchsia-400" />
            <span>Dept:</span>
          </div>
          <select
            value={filterDepartment}
            onChange={(e) => setFilterDepartment(e.target.value)}
            className="h-10 px-3 rounded-xl bg-background border border-border text-foreground text-xs font-bold outline-none cursor-pointer"
          >
            <option value="all">All Departments</option>
            {departments.map((dept) => (
              <option key={dept} value={dept}>
                {dept}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex flex-col items-center justify-center p-12 space-y-3 glass-card rounded-2xl border border-border">
          <Loader2 className="animate-spin size-8 text-fuchsia-400" />
          <p className="text-xs font-bold text-foreground">Loading job positions from database...</p>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && filteredJobs.length === 0 && (
        <div className="glass-card p-12 rounded-2xl border border-border text-center space-y-4 max-w-md mx-auto">
          <div className="size-14 rounded-2xl bg-fuchsia-600/15 text-fuchsia-400 flex items-center justify-center mx-auto border border-fuchsia-500/20">
            <Sparkles className="size-7" />
          </div>
          <h3 className="text-xl font-extrabold text-foreground">No Job Positions Found</h3>
          <p className="text-xs font-semibold text-foreground/80">
            {searchTerm || filterDepartment !== "all"
              ? "No jobs match your search criteria. Try adjusting filters."
              : "Post your first job opening to start matching candidate resumes."}
          </p>
          {isRecruiter && (
            <Button
              onClick={() => setIsModalOpen(true)}
              className="rounded-xl bg-fuchsia-600 hover:bg-fuchsia-700 text-white font-bold text-xs gap-2"
            >
              <Plus className="size-4" />
              <span>Post First Job</span>
            </Button>
          )}
        </div>
      )}

      {/* Job Grid */}
      {!isLoading && filteredJobs.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredJobs.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      )}

      {/* Create Job Modal */}
      <JobCreateModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  );
}
