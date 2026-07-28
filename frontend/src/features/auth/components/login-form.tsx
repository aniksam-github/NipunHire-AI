/**
 * LoginForm — email + password form with Zod validation.
 *
 * Designed with crystal-clear high-contrast typography, crisp placeholders,
 * and prominent labels for maximum visibility.
 */

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link } from "react-router-dom";
import { Loader2, Sparkles, Lock, Mail, ArrowLeft } from "lucide-react";

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

import { loginSchema, type LoginFormData } from "../types";
import { useLogin } from "../hooks/use-auth";

export function LoginForm() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const loginMutation = useLogin();

  const onSubmit = (data: LoginFormData) => {
    loginMutation.mutate(data);
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
          Recruiter Portal
        </span>
      </div>

      <Card className="w-full glass-card rounded-2xl border border-border shadow-2xl p-2 backdrop-blur-xl">
        <CardHeader className="text-center space-y-3 pb-2">
          <div className="size-12 rounded-2xl bg-fuchsia-600/20 border border-fuchsia-500/30 text-fuchsia-400 flex items-center justify-center mx-auto shadow-sm">
            <Sparkles className="size-6 text-fuchsia-300" />
          </div>
          <div className="space-y-1">
            <CardTitle className="text-2xl font-bold tracking-tight text-foreground">
              Welcome <span className="text-fuchsia-400">Back</span>
            </CardTitle>
            <CardDescription className="text-foreground/80 text-sm font-medium">
              Access your HireSense candidate evaluation suite
            </CardDescription>
          </div>
        </CardHeader>

        <CardContent className="pt-4">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Email */}
            <div className="space-y-2">
              <Label htmlFor="login-email" className="text-xs font-bold uppercase tracking-wider text-foreground">
                Email Address
              </Label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 size-4 text-fuchsia-400" />
                <Input
                  id="login-email"
                  type="email"
                  placeholder="ananya.sharma@techcorp.in"
                  autoComplete="email"
                  className="pl-10 h-11 bg-background border-border text-foreground placeholder:text-muted-foreground/90 focus:border-fuchsia-500 focus:ring-2 focus:ring-fuchsia-500/30 transition-all rounded-xl text-sm font-medium"
                  aria-invalid={!!errors.email}
                  {...register("email")}
                />
              </div>
              {errors.email && (
                <p className="text-xs font-semibold text-destructive">{errors.email.message}</p>
              )}
            </div>

            {/* Password */}
            <div className="space-y-2">
              <Label htmlFor="login-password" className="text-xs font-bold uppercase tracking-wider text-foreground">
                Account Password
              </Label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 size-4 text-fuchsia-400" />
                <Input
                  id="login-password"
                  type="password"
                  placeholder="Enter your passphrase"
                  autoComplete="current-password"
                  className="pl-10 h-11 bg-background border-border text-foreground placeholder:text-muted-foreground/90 focus:border-fuchsia-500 focus:ring-2 focus:ring-fuchsia-500/30 transition-all rounded-xl text-sm font-medium"
                  aria-invalid={!!errors.password}
                  {...register("password")}
                />
              </div>
              {errors.password && (
                <p className="text-xs font-semibold text-destructive">
                  {errors.password.message}
                </p>
              )}
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              className="w-full h-11 rounded-xl bg-fuchsia-600 hover:bg-fuchsia-700 text-white font-bold text-sm shadow-md transition-all mt-2"
              disabled={loginMutation.isPending}
            >
              {loginMutation.isPending ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="animate-spin size-4" />
                  <span>Authenticating...</span>
                </span>
              ) : (
                "Sign In to HireSense"
              )}
            </Button>
          </form>

          {/* Register link */}
          <p className="mt-6 text-center text-xs font-medium text-foreground/80">
            Don&apos;t have an account yet?{" "}
            <Link
              to="/register"
              className="font-bold text-fuchsia-400 hover:text-fuchsia-300 transition-colors underline underline-offset-2"
            >
              Create Account
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
