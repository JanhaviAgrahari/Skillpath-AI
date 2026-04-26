import React, { useState } from "react";
import { AppShell } from "./_shared/AppShell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { FileText, ClipboardPaste, BrainCircuit, Activity, ListChecks, CheckCircle2, Loader2 } from "lucide-react";
import { useNavigate } from "react-router-dom";

export function Landing() {
  const navigate = useNavigate();
  const [resumeText, setResumeText] = useState("");
  const [jdText, setJdText] = useState("");
  const [jobTitle, setJobTitle] = useState("Target Role");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const handleStartAssessment = async () => {
    if (!resumeText.trim() || resumeText.trim().length < 30) {
      setErrorMsg("Please paste your resume text (at least a few sentences).");
      return;
    }
    if (!jdText.trim()) {
      setErrorMsg("Please paste a job description.");
      return;
    }

    setIsSubmitting(true);
    setErrorMsg("");

    try {
      // 1. Create Session
      const sessionRes = await fetch("http://localhost:8000/api/v1/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_name: "Candidate User",
          target_role: jobTitle,
          experience_level: "mid"
        })
      });
      const sessionData = await sessionRes.json();
      if (!sessionData.success) throw new Error(sessionData.error_message || "Failed to create session");
      
      const sessionId = sessionData.data?.session_id || sessionData.session_id;
      
      // 2. Submit Resume as text (no file upload needed)
      const resumeFormData = new FormData();
      resumeFormData.append("resume_text", resumeText);
      
      const resumeRes = await fetch(`http://localhost:8000/api/v1/sessions/${sessionId}/resume`, {
        method: "POST",
        body: resumeFormData,
      });
      const resumeData = await resumeRes.json();
      if (!resumeData.success) throw new Error(resumeData.error_message || "Failed to submit resume");

      // 3. Submit JD
      const jdRes = await fetch(`http://localhost:8000/api/v1/sessions/${sessionId}/job-description`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: jobTitle,
          company_name: "Unknown",
          raw_text: jdText
        })
      });
      const jdData = await jdRes.json();
      if (!jdData.success) throw new Error(jdData.error_message || "Failed to submit JD");

      // Save session id to localStorage
      localStorage.setItem("session_id", sessionId);

      // 4. Trigger analysis run
      const analysisRes = await fetch(`http://localhost:8000/api/v1/sessions/${sessionId}/analysis/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      const analysisData = await analysisRes.json();
      if (!analysisData.success) throw new Error(analysisData.error_message || "Failed to run analysis");

      // Navigate to Assessment screen
      navigate("/assess");
      
    } catch (err) {
      setErrorMsg(err.message || "An unexpected error occurred.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AppShell currentStage="setup">
      <div className="max-w-4xl mx-auto py-12 px-6">
        <header className="mb-12">
          <h1 className="font-serif text-4xl font-normal tracking-tight text-foreground mb-4">
            Know exactly what you need to learn for the role you want.
          </h1>
          <p className="text-muted-foreground text-lg max-w-2xl leading-relaxed">
            Paste your resume and a job description. We'll assess your current proficiency, identify skill gaps, and build a targeted learning plan to get you interview-ready.
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          {/* Resume Text Input */}
          <div className="space-y-3">
            <h2 className="text-sm font-medium uppercase tracking-wider text-muted-foreground">1. Your Background</h2>
            <Card className="border-border/60 bg-card focus-within:ring-1 focus-within:ring-primary/30 transition-all duration-300 overflow-hidden flex flex-col">
              <div className="p-3 border-b border-border/50 bg-secondary/20 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ClipboardPaste className="size-4 text-muted-foreground" />
                  <span className="text-sm font-medium text-foreground">Resume</span>
                </div>
                {resumeText.trim().length >= 30 && (
                  <span className="inline-flex items-center gap-1 text-xs text-primary bg-primary/10 px-2 py-0.5 rounded-full">
                    <CheckCircle2 className="size-3" /> Ready
                  </span>
                )}
              </div>
              <Textarea 
                className="w-full min-h-[320px] resize-y border-0 focus-visible:ring-0 rounded-none bg-transparent p-4 text-sm leading-relaxed"
                placeholder="Paste your resume text here — work experience, skills, education, projects..."
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
              />
            </Card>
          </div>

          {/* Job Description Paste */}
          <div className="space-y-3">
            <h2 className="text-sm font-medium uppercase tracking-wider text-muted-foreground">2. Target Role</h2>
            <Card className="border-border/60 bg-card focus-within:ring-1 focus-within:ring-primary/30 transition-all duration-300 overflow-hidden flex flex-col">
              <div className="p-3 border-b border-border/50 bg-secondary/20 flex items-center justify-between">
                <input 
                  type="text" 
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  className="bg-transparent text-sm font-medium text-foreground focus:outline-none w-full" 
                  placeholder="Target Role (e.g. Senior Data Analyst)"
                />
                <span className="text-xs text-muted-foreground whitespace-nowrap bg-background/50 px-2 py-1 rounded-md ml-2 shrink-0">Pasted text</span>
              </div>
              <Textarea 
                className="w-full min-h-[320px] resize-y border-0 focus-visible:ring-0 rounded-none bg-transparent p-4 text-sm leading-relaxed"
                placeholder="Paste the job description here..."
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
              />
            </Card>
          </div>
        </div>
        
        {errorMsg && (
          <div className="text-center mb-6">
            <p className="text-sm text-destructive bg-destructive/10 inline-flex px-3 py-1.5 rounded-md font-medium">{errorMsg}</p>
          </div>
        )}

        <div className="flex justify-center mb-16">
          <Button 
            size="lg" 
            className="h-12 px-8 text-base shadow-sm group" 
            onClick={handleStartAssessment}
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 size-4 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                Start Assessment
                <BrainCircuit className="ml-2 size-4 group-hover:rotate-12 transition-transform" />
              </>
            )}
          </Button>
        </div>

        {/* How it works strip */}
        <div className="border-t border-border/50 pt-12">
          <h3 className="text-sm font-medium text-center text-muted-foreground mb-8">How the agent works</h3>
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-6 relative">
            <div className="hidden sm:block absolute top-5 left-[10%] right-[10%] h-px bg-border/40 -z-10" />
            
            <div className="flex flex-col items-center text-center gap-3">
              <div className="size-10 rounded-full bg-background border border-border flex items-center justify-center shadow-xs">
                <FileText className="size-4 text-muted-foreground" />
              </div>
              <div>
                <h4 className="text-sm font-medium text-foreground">Extract skills</h4>
                <p className="text-xs text-muted-foreground mt-1 max-w-[150px]">Identifies core requirements from the JD</p>
              </div>
            </div>

            <div className="flex flex-col items-center text-center gap-3">
              <div className="size-10 rounded-full bg-background border border-border flex items-center justify-center shadow-xs">
                <BrainCircuit className="size-4 text-muted-foreground" />
              </div>
              <div>
                <h4 className="text-sm font-medium text-foreground">Assess proficiency</h4>
                <p className="text-xs text-muted-foreground mt-1 max-w-[150px]">Asks targeted questions to gauge your level</p>
              </div>
            </div>

            <div className="flex flex-col items-center text-center gap-3">
              <div className="size-10 rounded-full bg-background border border-border flex items-center justify-center shadow-xs">
                <Activity className="size-4 text-muted-foreground" />
              </div>
              <div>
                <h4 className="text-sm font-medium text-foreground">Find gaps</h4>
                <p className="text-xs text-muted-foreground mt-1 max-w-[150px]">Maps your current skills against the role</p>
              </div>
            </div>

            <div className="flex flex-col items-center text-center gap-3">
              <div className="size-10 rounded-full bg-background border border-border flex items-center justify-center shadow-xs">
                <ListChecks className="size-4 text-muted-foreground" />
              </div>
              <div>
                <h4 className="text-sm font-medium text-foreground">Build plan</h4>
                <p className="text-xs text-muted-foreground mt-1 max-w-[150px]">Creates a week-by-week learning roadmap</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
