import React, { useState, useEffect } from "react";
import { AppShell } from "./_shared/AppShell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Download, Link as LinkIcon, Send, CheckCircle2, AlertCircle, ArrowUpRight, Award, MapPin, Loader2 } from "lucide-react";

export function Summary() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  
  const loadOrGenerateSummary = async (forceGenerate = false) => {
    try {
      const sessionId = localStorage.getItem("session_id");
      if (!sessionId) {
        setError("No session found. Please start from Setup.");
        setLoading(false);
        return;
      }

      if (forceGenerate) {
        setGenerating(true);
        const genRes = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/v1/sessions/${sessionId}/summary/generate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({})
        });
        const genData = await genRes.json();
        if (genData.success && genData.data) {
          setData(genData.data);
        } else {
          setError(genData.error_message || "Failed to generate summary.");
        }
      } else {
        const getRes = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/v1/sessions/${sessionId}/summary`);
        const getData = await getRes.json();
        if (getData.success && getData.data) {
          setData(getData.data);
        } else {
          loadOrGenerateSummary(true);
          return;
        }
      }
    } catch (err) {
      setError(err.message || "Network error loading summary.");
    } finally {
      setLoading(false);
      setGenerating(false);
    }
  };

  useEffect(() => {
    loadOrGenerateSummary();
  }, []);

  const handleExport = async () => {
    try {
      const sessionId = localStorage.getItem("session_id");
      const res = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/v1/sessions/${sessionId}/export`);
      const exportData = await res.json();
      
      if (exportData.success) {
        // Trigger generic JSON download to mock the PDF/export functionality as described in guide
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportData.data, null, 2));
        const anchor = document.createElement('a');
        anchor.setAttribute("href", dataStr);
        anchor.setAttribute("download", `skillpath_report_${sessionId}.json`);
        document.body.appendChild(anchor);
        anchor.click();
        anchor.remove();
      } else {
        alert("Failed to export: " + (exportData.error_message || "Unknown error"));
      }
    } catch(err) {
      alert("Error exporting report: " + err.message);
    }
  };

  if (loading || generating) {
    return (
      <AppShell currentStage="report">
        <div className="flex h-[80vh] items-center justify-center flex-col">
          <Loader2 className="size-8 text-primary animate-spin mb-4" />
          <p className="text-muted-foreground font-medium">
            {generating ? "Synthesizing your final report..." : "Loading report..."}
          </p>
        </div>
      </AppShell>
    );
  }

  if (error) {
    return (
      <AppShell currentStage="report">
        <div className="flex h-[80vh] items-center justify-center flex-col">
          <AlertCircle className="size-10 text-destructive mb-4" />
          <p className="text-muted-foreground font-medium mb-4">{error}</p>
          <Button onClick={() => loadOrGenerateSummary(true)}>Retry Generate</Button>
        </div>
      </AppShell>
    );
  }

  const candidateProfile = data?.candidate_profile || {};
  const roleSummary = data?.role_summary || {};
  const highlights = data?.highlights || {};
  const assessmentSummary = data?.assessment_summary || {};
  const planSummary = data?.learning_plan_summary || {};
  
  const userName = candidateProfile.name || "Candidate Name";
  const userInitials = userName.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase() || "CN";
  const targetRole = roleSummary.target_role || "Target Role";
  const matchScore = roleSummary.overall_match_score || "0";

  // Use the array or fallback text
  const strongestSkillStr = Array.isArray(highlights.strongest_skills) ? highlights.strongest_skills.join(", ") : highlights.strongest_skills || "Not assessed";
  const biggestGapStr = Array.isArray(highlights.main_gaps) ? highlights.main_gaps.join(", ") : highlights.main_gaps || "None identified";
  const topMilestones = Array.isArray(planSummary.top_milestones) ? planSummary.top_milestones : [];
  const nextSteps = data?.recommended_next_steps || [];

  return (
    <AppShell currentStage="report">
      <div className="max-w-4xl mx-auto py-10 px-6">
        
        {/* Actions */}
        <div className="flex justify-end mb-6 gap-2">
          <Button variant="outline" size="sm" className="h-8" onClick={() => navigator.clipboard.writeText(window.location.href)}>
            <LinkIcon className="size-3.5 mr-2" /> Copy Link
          </Button>
          <Button variant="outline" size="sm" className="h-8">
            <Send className="size-3.5 mr-2" /> Send to Mentor
          </Button>
          <Button size="sm" className="h-8 shadow-sm" onClick={handleExport}>
            <Download className="size-3.5 mr-2" /> Download Report
          </Button>
        </div>

        {/* Document Container */}
        <div className="bg-card rounded-xl border border-border/50 shadow-sm overflow-hidden">
          
          {/* Profile Header */}
          <div className="p-8 border-b border-border/50 bg-secondary/10 flex flex-col sm:flex-row sm:items-center justify-between gap-6">
            <div className="flex items-center gap-5">
              <div className="size-16 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center text-primary font-serif text-2xl tracking-tight">
                {userInitials}
              </div>
              <div>
                <h1 className="text-2xl font-serif text-foreground mb-1">{userName}</h1>
                <p className="text-sm text-muted-foreground">Target Role: <span className="font-medium text-foreground">{targetRole}</span></p>
                {candidateProfile.experience_level && (
                    <p className="text-xs text-muted-foreground mt-1 capitalize">Experience Level: {candidateProfile.experience_level}</p>
                )}
              </div>
            </div>
            <div className="text-right shrink-0">
              <div className="inline-flex flex-col items-center justify-center bg-background border border-border rounded-lg p-3 min-w-[120px] shadow-sm">
                <span className="text-[10px] uppercase tracking-wider text-muted-foreground font-medium mb-1">Role Match</span>
                <span className="text-2xl font-serif text-primary">{matchScore}%</span>
                <span className="text-[10px] text-muted-foreground mt-1">{roleSummary.fit_label}</span>
              </div>
            </div>
          </div>

          <div className="p-8 space-y-10">
            
            {/* Key Findings */}
            <section>
              <h2 className="text-xs font-medium uppercase tracking-widest text-muted-foreground mb-4">Key Findings</h2>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="p-4 rounded-lg bg-emerald-500/5 border border-emerald-500/10">
                  <div className="flex items-center gap-2 mb-2 text-emerald-700">
                    <Award className="size-4" />
                    <span className="text-sm font-medium">Strongest Area</span>
                  </div>
                  <p className="text-sm text-foreground">{strongestSkillStr}</p>
                </div>
                <div className="p-4 rounded-lg bg-destructive/5 border border-destructive/10">
                  <div className="flex items-center gap-2 mb-2 text-destructive">
                    <AlertCircle className="size-4" />
                    <span className="text-sm font-medium">Biggest Gap</span>
                  </div>
                  <p className="text-sm text-foreground">{biggestGapStr}</p>
                </div>
                <div className="p-4 rounded-lg bg-primary/5 border border-primary/10">
                  <div className="flex items-center gap-2 mb-2 text-primary">
                    <MapPin className="size-4" />
                    <span className="text-sm font-medium">Next Step</span>
                  </div>
                  <p className="text-sm text-foreground">
                      {nextSteps.length > 0 ? nextSteps[0] : "Proceed with the recommended learning plan milestones."}
                  </p>
                </div>
              </div>
            </section>

            {/* Recommendation Narrative */}
            <section>
              <h2 className="text-xs font-medium uppercase tracking-widest text-muted-foreground mb-4">Agent's Evaluation</h2>
              <div className="prose prose-sm max-w-none text-foreground leading-relaxed whitespace-pre-wrap">
                {roleSummary.explanation ? (
                  <p className="mb-4">{roleSummary.explanation}</p>
                ) : null}
                {assessmentSummary.explanation ? (
                  <p className="mb-4">{assessmentSummary.explanation}</p>
                ) : null}
                {planSummary.explanation ? (
                  <p>{planSummary.explanation}</p>
                ) : null}
                {!roleSummary.explanation && !assessmentSummary.explanation && !planSummary.explanation && (
                  <p>A comprehensive narrative summarizing the candidate's core strengths, assessment results, and alignment to the targeted position is being rendered based on the deep skill analysis.</p>
                )}
              </div>
            </section>

            {/* Condensed Plan Recap */}
            <section>
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xs font-medium uppercase tracking-widest text-muted-foreground">Recommended Action Plan</h2>
                    {planSummary.total_weeks && <span className="text-xs text-muted-foreground font-medium">{planSummary.total_weeks} weeks • {planSummary.total_hours} hours total</span>}
                </div>
              <Card className="border-border/50 shadow-none overflow-hidden">
                <div className="divide-y divide-border/50">
                  {topMilestones.length > 0 ? topMilestones.map((milestone, idx) => (
                    <div key={idx} className="p-4 flex items-center justify-between hover:bg-secondary/20 transition-colors">
                      <div className="flex items-center gap-4">
                        <span className="text-sm font-medium w-16 text-muted-foreground shrink-0">{milestone.timeframe || `Phase ${idx+1}`}</span>
                        <span className="text-sm text-foreground">{milestone.title || milestone.focus || milestone}</span>
                      </div>
                      {milestone.hours && <span className="text-xs text-muted-foreground shrink-0">{milestone.hours} hours</span>}
                    </div>
                  )) : (
                      <div className="p-4 text-center text-sm text-muted-foreground">No specific milestones found in summary.</div>
                  )}
                </div>
              </Card>
            </section>

          </div>
        </div>

      </div>
    </AppShell>
  );
}
