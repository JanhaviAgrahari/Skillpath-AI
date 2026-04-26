import React, { useState, useEffect } from "react";
import { AppShell } from "./_shared/AppShell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Target, CheckCircle2, AlertCircle, HelpCircle, ArrowRight, BarChart3, TrendingUp, Loader2 } from "lucide-react";
import { useNavigate } from "react-router-dom";

export function Analysis() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        const sessionId = localStorage.getItem("session_id");
        if (!sessionId) {
          setError("No active session found. Please start from the setup page.");
          setLoading(false);
          return;
        }

        const res = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/v1/sessions/${sessionId}/analysis/complete`);
        const result = await res.json();

        if (result.success && result.data) {
          setData(result.data);
        } else {
          setError(result.error_message || "Failed to load analysis data.");
        }
      } catch (err) {
        setError(err.message || "Network error while fetching analysis.");
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, []);

  if (loading) {
    return (
      <AppShell currentStage="analyse">
        <div className="flex h-[80vh] items-center justify-center flex-col">
          <Loader2 className="size-8 text-primary animate-spin mb-4" />
          <p className="text-muted-foreground font-medium">Loading your deep skill analysis...</p>
        </div>
      </AppShell>
    );
  }

  if (error) {
    return (
      <AppShell currentStage="analyse">
        <div className="flex h-[80vh] items-center justify-center flex-col">
          <AlertCircle className="size-10 text-destructive mb-4" />
          <p className="text-muted-foreground font-medium mb-4">{error}</p>
          <Button onClick={() => navigate("/")}>Return to Setup</Button>
        </div>
      </AppShell>
    );
  }

  const analysisResult = data?.result || {};
  const roleMatchScore = Math.round(analysisResult.role_match_score || 0);
  const roleMatchLabel = analysisResult.role_match_label || "Needs Assessment";
  const explanation = analysisResult.explanation_summary || "";

  const strongMatches = analysisResult.strong_matches || [];
  const partialMatches = analysisResult.partial_matches || [];
  const missingSkills = analysisResult.missing_skills || [];
  const adjacentSkills = analysisResult.adjacent_skills || [];

  const jdName = data?.jd_snapshot?.title || "Target Role";

  const coreMatched = strongMatches.length + partialMatches.length;
  const coreTotal = coreMatched + missingSkills.length;

  const missingCount = missingSkills.length;
  const weeksToReady = Math.max(1, missingCount * 2);

  const handleGoToPlan = () => {
    navigate("/plan");
  };

  return (
    <AppShell currentStage="analyse">
      <div className="max-w-5xl mx-auto py-10 px-6">

        {/* Header */}
        <header className="mb-10 flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div>
            <h1 className="font-serif text-3xl font-normal tracking-tight text-foreground mb-2">
              Skill Analysis
            </h1>
            <p className="text-muted-foreground">
              Comparing your profile against <span className="font-medium text-foreground">{jdName}</span>
            </p>
          </div>
          <Button onClick={handleGoToPlan}>
            View Learning Plan <ArrowRight className="ml-2 size-4" />
          </Button>
        </header>

        {/* Top Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-10">
          <Card className="p-5 border-primary/20 bg-primary/5 flex flex-col justify-center relative overflow-hidden">
            <div className="absolute right-0 bottom-0 opacity-10 translate-x-1/4 translate-y-1/4">
              <Target className="size-32" />
            </div>
            <span className="text-sm font-medium text-primary mb-1">Role Match</span>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-serif tracking-tight text-foreground">{roleMatchScore}%</span>
              <span className="text-xs text-primary font-medium">{roleMatchLabel}</span>
            </div>
          </Card>
          <Card className="p-5 flex flex-col justify-center">
            <span className="text-sm font-medium text-muted-foreground mb-1">Core Skills</span>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-serif tracking-tight text-foreground">{coreMatched}</span>
              <span className="text-xs text-muted-foreground">/ {coreTotal || 1} covered</span>
            </div>
          </Card>
          <Card className="p-5 flex flex-col justify-center">
            <span className="text-sm font-medium text-muted-foreground mb-1">Missing Skills</span>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-serif tracking-tight text-foreground">{missingCount}</span>
              <span className="text-xs text-muted-foreground">critical gaps</span>
            </div>
          </Card>
          <Card className="p-5 flex flex-col justify-center">
            <span className="text-sm font-medium text-muted-foreground mb-1">Est. Time to Ready</span>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-serif tracking-tight text-foreground">{weeksToReady}</span>
              <span className="text-xs text-muted-foreground">weeks</span>
            </div>
          </Card>
        </div>

        {/* Matrix & Explanation Split */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">

          <div className="lg:col-span-2 space-y-6">
            <h2 className="text-lg font-medium font-serif flex items-center gap-2">
              <BarChart3 className="size-5 text-primary" />
              Skill Matrix
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">

              {/* Strong Match */}
              <div className="space-y-3">
                <h3 className="text-xs font-medium uppercase tracking-wider text-emerald-600 flex items-center gap-1.5">
                  <CheckCircle2 className="size-3.5" /> Strong Match
                </h3>
                {strongMatches.length === 0 ? (
                  <p className="text-sm text-muted-foreground italic">None detected</p>
                ) : (
                  <div className="space-y-2">
                    {strongMatches.map((item, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 rounded-lg border border-border/50 bg-card shadow-sm">
                        <span className="text-sm font-medium">{item.skill?.canonical_name || item.skill?.name || 'Skill'}</span>
                        <Badge variant="outline" className="bg-emerald-500/10 text-emerald-600 border-emerald-200" title={item.reason}>
                          {Math.round((item.score || 0) * 100)}%
                        </Badge>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Partial Match */}
              <div className="space-y-3">
                <h3 className="text-xs font-medium uppercase tracking-wider text-amber-600 flex items-center gap-1.5">
                  <TrendingUp className="size-3.5" /> Partial Match
                </h3>
                {partialMatches.length === 0 ? (
                  <p className="text-sm text-muted-foreground italic">None detected</p>
                ) : (
                  <div className="space-y-2">
                    {partialMatches.map((item, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 rounded-lg border border-border/50 bg-card shadow-sm">
                        <span className="text-sm font-medium">{item.skill?.canonical_name || item.skill?.name || 'Skill'}</span>
                        <Badge variant="outline" className="bg-amber-500/10 text-amber-600 border-amber-200" title={item.reason}>
                          {Math.round((item.score || 0) * 100)}%
                        </Badge>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Missing */}
              <div className="space-y-3">
                <h3 className="text-xs font-medium uppercase tracking-wider text-destructive flex items-center gap-1.5">
                  <AlertCircle className="size-3.5" /> Missing
                </h3>
                {missingSkills.length === 0 ? (
                  <p className="text-sm text-muted-foreground italic">None detected</p>
                ) : (
                  <div className="space-y-2">
                    {missingSkills.map((item, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 rounded-lg border border-destructive/20 bg-destructive/5 shadow-sm min-h-12">
                        <span className="text-sm font-medium pr-2">{item.skill?.canonical_name || item.skill?.name || 'Skill'}</span>
                        <span className="size-2 rounded-full bg-destructive shrink-0" title={item.reason || "Required by JD"} />
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Need Verification / Adjacent */}
              <div className="space-y-3">
                <h3 className="text-xs font-medium uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                  <HelpCircle className="size-3.5" /> Nice to have / Adjacent
                </h3>
                {adjacentSkills.length === 0 ? (
                  <p className="text-sm text-muted-foreground italic">None detected</p>
                ) : (
                  <div className="space-y-2">
                    {adjacentSkills.map((item, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 rounded-lg border border-border/50 bg-secondary/30 shadow-sm text-muted-foreground min-h-12">
                        <span className="text-sm font-medium pr-2">{item.skill?.canonical_name || item.skill?.name || 'Skill'}</span>
                        <span className="text-xs shrink-0" title={item.reason}>Suggested</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

            </div>
          </div>

          <div className="space-y-6">
            <Card className="p-6 h-full flex flex-col bg-secondary/10 border-border/60">
              <h3 className="text-sm font-medium text-foreground mb-4">Why {roleMatchScore}% Match?</h3>
              <div className="space-y-4 text-sm text-muted-foreground leading-relaxed flex-1 whitespace-pre-wrap">
                {explanation || "Your detailed analysis explanation will appear here once the assessment fully synthesizes your background against the specific job criteria."}
              </div>
              <div className="mt-6 pt-4 border-t border-border/50">
                <p className="text-xs font-medium text-foreground mb-2">Recommendation</p>
                <p className="text-xs text-muted-foreground italic">
                  Focus on the primary gaps identified in the missing skills section to increase your readiness. View the complete learning plan for actionable steps.
                </p>
              </div>
            </Card>
          </div>

        </div>

      </div>
    </AppShell>
  );
}
