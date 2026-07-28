/**
 * RegisterForm — registration form with interactive password criteria indicators.
 *
 * Designed with crystal-clear high-contrast typography, crisp placeholders,
 * and prominent labels for maximum visibility.
 */

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link } from "react-router-dom";
import { Loader2, Sparkles, User as UserIcon, Mail, Lock, Briefcase, UserCheck, CheckCircle2, Circle, ArrowLeft } from "lucide-react";

import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/shared/components/ui/card";

import { registerSchema, type RegisterFormData } from "../types";
import { useRegister } from "../hooks/use-auth";

export function RegisterForm() {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      full_name: "",
      email: "",
      password: "",
      confirm_password: "",
      role: "recruiter",
    },
  });

  const registerMutation = useRegister();
  
  // Watch values for dynamic UI & real-time criteria checking
  const selectedRole = watch("role");
  const watchedPassword = watch("password") || "";
  const watchedConfirm = watch("confirm_password") || "";

  // Password criteria logic
  const hasMinLength = watchedPassword.length >= 8;
  const hasLetter = /[a-zA-Z]/.test(watchedPassword);
  const hasNumberOrSymbol = /[0-9!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(watchedPassword);
  const passwordsMatch = watchedPassword.length > 0 && watchedPassword === watchedConfirm;

  const onSubmit = (data: RegisterFormData) => {
    registerMutation.mutate(data);
  };

  return (
    <div className="w-full max-w-md space-y-4">
      {/* Home Navigation Link */}
      <div className="flex items-center justify-between px-1">
        <Link
          to="/"
          className="inline-flex items-center gap-2 text-sm font-semibold text-fuchsia-400 hover:text-fuchsia-300 transition-colors"
        >
          <ArrowLeft className="size-4" />
          <span>Back to Home</span>
        </Link>
        <span className="text-xs font-semibold text-foreground/80 uppercase tracking-wider">
          New Account Registration
        </span>
      </div>

      <Card className="w-full glass-card rounded-2xl border border-border shadow-2xl p-2 backdrop-blur-xl">
        <CardHeader className="text-center space-y-3 pb-2">
          <div className="size-12 rounded-2xl bg-fuchsia-600/20 border border-fuchsia-500/30 text-fuchsia-400 flex items-center justify-center mx-auto shadow-sm">
            <Sparkles className="size-6 text-fuchsia-300" />
          </div>
          <div className="space-y-1">
            <CardTitle className="text-2xl font-bold tracking-tight text-foreground">
              Create Your <span className="text-fuchsia-400">Account</span>
            </CardTitle>
            <CardDescription className="text-foreground/80 text-sm font-medium">
              Join HireSense AI to evaluate candidates with precision
            </CardDescription>
          </div>
        </CardHeader>

        <CardContent className="pt-4">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-3.5">
            {/* Full Name */}
            <div className="space-y-1.5">
              <Label htmlFor="register-name" className="text-xs font-bold uppercase tracking-wider text-foreground">
                Full Name
              </Label>
              <div className="relative">
                <UserIcon className="absolute left-3.5 top-1/2 -translate-y-1/2 size-4 text-fuchsia-400" />
                <Input
                  id="register-name"
                  type="text"
                  placeholder="Ananya Sharma"
                  autoComplete="name"
                  className="pl-10 h-10 bg-background border-border text-foreground placeholder:text-muted-foreground/90 focus:border-fuchsia-500 focus:ring-2 focus:ring-fuchsia-500/30 transition-all rounded-xl text-sm font-medium"
                  aria-invalid={!!errors.full_name}
                  {...register("full_name")}
                />
              </div>
              {errors.full_name && (
                <p className="text-xs font-semibold text-destructive">{errors.full_name.message}</p>
              )}
            </div>

            {/* Email */}
            <div className="space-y-1.5">
              <Label htmlFor="register-email" className="text-xs font-bold uppercase tracking-wider text-foreground">
                {selectedRole === "recruiter" ? "Work Email Address" : "Email Address"}
              </Label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 size-4 text-fuchsia-400" />
                <Input
                  id="register-email"
                  type="email"
                  placeholder={selectedRole === "recruiter" ? "ananya.sharma@techcorp.in" : "ananya.sharma@gmail.com"}
                  autoComplete="email"
                  className="pl-10 h-10 bg-background border-border text-foreground placeholder:text-muted-foreground/90 focus:border-fuchsia-500 focus:ring-2 focus:ring-fuchsia-500/30 transition-all rounded-xl text-sm font-medium"
                  aria-invalid={!!errors.email}
                  {...register("email")}
                />
              </div>
              {errors.email && (
                <p className="text-xs font-semibold text-destructive">{errors.email.message}</p>
              )}
            </div>

            {/* Password */}
            <div className="space-y-1.5">
              <Label htmlFor="register-password" className="text-xs font-bold uppercase tracking-wider text-foreground">
                Password
              </Label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 size-4 text-fuchsia-400" />
                <Input
                  id="register-password"
                  type="password"
                  placeholder="e.g. Passphrase#2026"
                  autoComplete="new-password"
                  className="pl-10 h-10 bg-background border-border text-foreground placeholder:text-muted-foreground/90 focus:border-fuchsia-500 focus:ring-2 focus:ring-fuchsia-500/30 transition-all rounded-xl text-sm font-medium"
                  aria-invalid={!!errors.password}
                  {...register("password")}
                />
              </div>
              {errors.password && (
                <p className="text-xs font-semibold text-destructive">{errors.password.message}</p>
              )}
            </div>

            {/* Confirm Password */}
            <div className="space-y-1.5">
              <Label htmlFor="register-confirm" className="text-xs font-bold uppercase tracking-wider text-foreground">
                Confirm Password
              </Label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 size-4 text-fuchsia-400" />
                <Input
                  id="register-confirm"
                  type="password"
                  placeholder="Re-enter your password"
                  autoComplete="new-password"
                  className="pl-10 h-10 bg-background border-border text-foreground placeholder:text-muted-foreground/90 focus:border-fuchsia-500 focus:ring-2 focus:ring-fuchsia-500/30 transition-all rounded-xl text-sm font-medium"
                  aria-invalid={!!errors.confirm_password}
                  {...register("confirm_password")}
                />
              </div>
              {errors.confirm_password && (
                <p className="text-xs font-semibold text-destructive">
                  {errors.confirm_password.message}
                </p>
              )}
            </div>

            {/* Interactive Password Criteria Box */}
            <div className="p-3.5 rounded-xl bg-secondary/80 border border-border space-y-2 text-xs">
              <p className="font-bold text-xs uppercase tracking-wider text-foreground">Password Criteria Checklist</p>
              <div className="grid grid-cols-2 gap-2 pt-0.5">
                <div className={`flex items-center gap-1.5 ${hasMinLength ? "text-emerald-400 font-bold" : "text-foreground/70"}`}>
                  {hasMinLength ? <CheckCircle2 className="size-4 text-emerald-400" /> : <Circle className="size-4 opacity-50" />}
                  <span>8+ Characters</span>
                </div>
                <div className={`flex items-center gap-1.5 ${hasLetter ? "text-emerald-400 font-bold" : "text-foreground/70"}`}>
                  {hasLetter ? <CheckCircle2 className="size-4 text-emerald-400" /> : <Circle className="size-4 opacity-50" />}
                  <span>Letter Included</span>
                </div>
                <div className={`flex items-center gap-1.5 ${hasNumberOrSymbol ? "text-emerald-400 font-bold" : "text-foreground/70"}`}>
                  {hasNumberOrSymbol ? <CheckCircle2 className="size-4 text-emerald-400" /> : <Circle className="size-4 opacity-50" />}
                  <span>Number / Symbol</span>
                </div>
                <div className={`flex items-center gap-1.5 ${passwordsMatch ? "text-emerald-400 font-bold" : "text-foreground/70"}`}>
                  {passwordsMatch ? <CheckCircle2 className="size-4 text-emerald-400" /> : <Circle className="size-4 opacity-50" />}
                  <span>Passwords Match</span>
                </div>
              </div>
            </div>

            {/* Role Selector Pill */}
            <div className="space-y-2 pt-1">
              <Label className="text-xs font-bold uppercase tracking-wider text-foreground">
                Account Role
              </Label>
              <div className="grid grid-cols-2 gap-2.5">
                <label
                  htmlFor="role-recruiter"
                  className="flex cursor-pointer items-center justify-center gap-2 rounded-xl border border-border bg-background px-3 py-2.5 text-xs font-bold transition-all hover:bg-accent has-[:checked]:border-fuchsia-500 has-[:checked]:bg-fuchsia-500/15 has-[:checked]:text-fuchsia-300 shadow-sm"
                >
                  <input
                    type="radio"
                    id="role-recruiter"
                    value="recruiter"
                    className="sr-only"
                    {...register("role")}
                  />
                  <Briefcase className="size-4" />
                  <span>Recruiter</span>
                </label>

                <label
                  htmlFor="role-candidate"
                  className="flex cursor-pointer items-center justify-center gap-2 rounded-xl border border-border bg-background px-3 py-2.5 text-xs font-bold transition-all hover:bg-accent has-[:checked]:border-fuchsia-500 has-[:checked]:bg-fuchsia-500/15 has-[:checked]:text-fuchsia-300 shadow-sm"
                >
                  <input
                    type="radio"
                    id="role-candidate"
                    value="candidate"
                    className="sr-only"
                    {...register("role")}
                  />
                  <UserCheck className="size-4" />
                  <span>Candidate</span>
                </label>
              </div>
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              className="w-full h-11 rounded-xl bg-fuchsia-600 hover:bg-fuchsia-700 text-white font-bold text-sm shadow-md transition-all mt-2"
              disabled={registerMutation.isPending}
            >
              {registerMutation.isPending ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="animate-spin size-4" />
                  <span>Creating Account...</span>
                </span>
              ) : (
                "Create Account"
              )}
            </Button>
          </form>

          {/* Login link */}
          <p className="mt-4 text-center text-xs font-medium text-foreground/80">
            Already have an account?{" "}
            <Link
              to="/login"
              className="font-bold text-fuchsia-400 hover:text-fuchsia-300 transition-colors underline underline-offset-2"
            >
              Sign In
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
