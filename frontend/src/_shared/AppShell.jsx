import React from "react";
import { cn } from "@/lib/utils";
import { Link } from "react-router-dom";
import { FileText, BrainCircuit, Activity, ListChecks, CheckSquare } from "lucide-react";

export function AppShell({ children, currentStage = "setup" }) {
  const steps = [
    { id: "setup", label: "Setup", icon: FileText, path: "/" },
    { id: "assess", label: "Assess", icon: BrainCircuit, path: "/assess" },
    { id: "analyse", label: "Analyse", icon: Activity, path: "/analyse" },
    { id: "plan", label: "Plan", icon: ListChecks, path: "/plan" },
    { id: "report", label: "Report", icon: CheckSquare, path: "/report" },
  ];

  return (
    <div className="min-h-screen bg-background flex flex-col md:flex-row">
      <aside className="w-full md:w-64 border-r border-border bg-card flex flex-col relative flex-shrink-0 min-h-screen">
        <div className="p-6">
          <div className="flex items-center gap-2 mb-8">
            <div className="size-6 bg-primary rounded" />
            <span className="font-bold text-xl tracking-tight text-primary">Skillpath</span>
          </div>

          <div className="mb-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            WORKFLOW
          </div>

          <nav className="space-y-1">
            {steps.map((step) => {
              const active = currentStage === step.id;
              const Icon = step.icon;
              return (
                <Link
                  key={step.id}
                  to={step.path}
                  className={cn(
                    "flex items-center justify-between px-3 py-2 rounded-md text-sm transition-colors",
                    active
                      ? "bg-secondary text-secondary-foreground font-medium"
                      : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground"
                  )}
                >
                  <div className="flex items-center gap-3">
                    <Icon className="size-4" />
                    {step.label}
                  </div>
                  {active && <div className="size-1.5 rounded-full bg-primary" />}
                </Link>
              );
            })}
          </nav>
        </div>



      </aside>

      <main className="flex-1 bg-background overflow-auto">
        {children}
      </main>
    </div>
  );
}
