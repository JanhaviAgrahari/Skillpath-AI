import React, { useState, useEffect } from "react";
import { AppShell } from "./_shared/AppShell";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { PlayCircle, BookOpen, Layers, RefreshCw, Calendar, ArrowRight, Loader2, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { useNavigate } from "react-router-dom";

export function Plan() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [intensity, setIntensity] = useState("standard");
  const [checkedTasks, setCheckedTasks] = useState({}); // Local state for checked tasks

  const loadOrGeneratePlan = async (forceGenerate = false, targetIntensity = "standard") => {
    try {
      const sessionId = localStorage.getItem("session_id");
      if (!sessionId) {
        setError("No session found. Start from Setup.");
        setLoading(false);
        return;
      }

      if (forceGenerate) {
        setGenerating(true);
        const genRes = await fetch(`http://localhost:8000/api/v1/sessions/${sessionId}/learning-plan/generate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            weeks: 4,
            hours_per_week: targetIntensity === 'intensive' ? 10 : (targetIntensity === 'gentle' ? 3 : 5),
            intensity: targetIntensity
          })
        });
        const genData = await genRes.json();
        if (genData.success && genData.data) {
          setData(genData.data);
        } else {
          setError(genData.error_message || "Failed to generate learning plan.");
        }
        setGenerating(false);
        setLoading(false);
      } else {
        // Try GET first
        const getRes = await fetch(`http://localhost:8000/api/v1/sessions/${sessionId}/learning-plan`);
        if (getRes.ok) {
          const getData = await getRes.json();
          if (getData.success && getData.data) {
            setData(getData.data);
            setIntensity(getData.data.overview?.intensity || "standard");
            setLoading(false);
            return;
          }
        }
        // If 404 or fails, auto-generate
        await loadOrGeneratePlan(true, intensity);
      }
    } catch (err) {
      setError(err.message || "Network error loading plan.");
      setLoading(false);
      setGenerating(false);
    }
  };

  useEffect(() => {
    loadOrGeneratePlan(false, intensity);
  }, []);

  const handleRegenerate = async (newIntensity) => {
    const target = newIntensity || intensity;
    setIntensity(target);
    await loadOrGeneratePlan(true, target);
  };

  const toggleTask = (taskId) => {
    setCheckedTasks(prev => ({ ...prev, [taskId]: !prev[taskId] }));
  };

  if (loading || generating) {
    return (
      <AppShell currentStage="plan">
        <div className="flex h-[80vh] items-center justify-center flex-col">
          <Loader2 className="size-8 text-primary animate-spin mb-4" />
          <p className="text-muted-foreground font-medium">
            {generating ? "Building your personalized roadmap..." : "Loading learning plan..."}
          </p>
        </div>
      </AppShell>
    );
  }

  if (error) {
    return (
      <AppShell currentStage="plan">
        <div className="flex h-[80vh] items-center justify-center flex-col">
          <AlertCircle className="size-10 text-destructive mb-4" />
          <p className="text-muted-foreground font-medium mb-4">{error}</p>
          <Button onClick={() => handleRegenerate(intensity)}>Retry Generate</Button>
        </div>
      </AppShell>
    );
  }

  const overview = data?.overview || {};
  const milestones = data?.milestones || [];

  return (
    <AppShell currentStage="plan">
      <div className="max-w-4xl mx-auto py-10 px-6">
        
        {/* Header & Controls */}
        <header className="mb-12 flex flex-col md:flex-row md:items-start justify-between gap-6">
          <div>
            <h1 className="font-serif text-3xl font-normal tracking-tight text-foreground mb-3">
              Your Learning Roadmap
            </h1>
            <p className="text-muted-foreground flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center rounded-md bg-secondary px-2 py-1 text-xs font-medium">
                Estimated {overview.estimated_total_hours} hours
              </span>
              <span>over {milestones.length} weeks to close skill gaps.</span>
            </p>
            {overview.goal && (
              <p className="text-sm text-muted-foreground mt-2 max-w-2xl">{overview.goal}</p>
            )}
          </div>
          
          <div className="flex items-center gap-3 shrink-0">
            <div className="flex items-center rounded-lg border border-border p-1 bg-card shadow-sm">
              <button 
                onClick={() => handleRegenerate("gentle")}
                className={cn(
                  "px-3 py-1.5 text-xs font-medium rounded-md transition-colors",
                  intensity === "gentle" ? "bg-primary text-primary-foreground shadow-xs" : "text-muted-foreground hover:text-foreground"
                )}
              >
                Gentle
              </button>
              <button 
                onClick={() => handleRegenerate("standard")}
                className={cn(
                  "px-3 py-1.5 text-xs font-medium rounded-md transition-colors",
                  intensity === "standard" ? "bg-primary text-primary-foreground shadow-xs" : "text-muted-foreground hover:text-foreground"
                )}
              >
                Standard
              </button>
              <button 
                onClick={() => handleRegenerate("intensive")}
                className={cn(
                  "px-3 py-1.5 text-xs font-medium rounded-md transition-colors",
                  intensity === "intensive" ? "bg-primary text-primary-foreground shadow-xs" : "text-muted-foreground hover:text-foreground"
                )}
              >
                Intensive
              </button>
            </div>
            <Button variant="outline" size="icon" title="Regenerate plan" onClick={() => handleRegenerate()}>
              <RefreshCw className="size-4" />
            </Button>
          </div>
        </header>

        {/* Timeline */}
        <div className="space-y-12 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-border before:via-border/50 before:to-transparent">
          
          {milestones.length === 0 && (
             <p className="text-center text-muted-foreground">No milestones generated.</p>
          )}

          {milestones.map((ms, index) => {
            const isCompleted = index === 0 && milestones.length > 1; // Just simulating state for first week
            const isCurrent = index === 1 || (index === 0 && milestones.length === 1);
            
            return (
              <div key={index} className={cn(
                "relative flex items-center justify-between md:justify-normal group",
                index % 2 !== 0 ? "md:flex-row-reverse" : ""
              )}>
                
                {/* Timeline Node */}
                <div className={cn(
                  "flex items-center justify-center size-10 rounded-full border-4 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10",
                  isCompleted ? "border-background bg-primary text-primary-foreground" :
                  isCurrent ? "border-background bg-card border-primary text-primary" : 
                  "border-background bg-card text-muted-foreground border-border"
                )}>
                  <span className="text-sm font-bold">W{ms.week}</span>
                </div>
                
                {/* Content Card */}
                <div className={cn(
                  "w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)]",
                  isCompleted ? "opacity-70" : ""
                )}>
                  <div className="mb-2 flex items-center justify-between">
                    <span className={cn(
                      "text-xs font-medium uppercase tracking-wider",
                      isCurrent ? "text-primary" : "text-muted-foreground"
                    )}>
                      {ms.title}
                    </span>
                    <Badge variant={isCurrent ? "secondary" : "outline"} className={cn(
                      "text-[10px]", 
                      isCurrent ? "bg-primary/10 text-primary hover:bg-primary/20" : ""
                    )}>
                      {ms.estimated_hours} hours
                    </Badge>
                  </div>

                  <Card className={cn(
                    "overflow-hidden shadow-sm transition-opacity",
                    isCurrent ? "p-0 border-primary/30 shadow-md bg-card" : 
                    isCompleted ? "p-4 border-border bg-card" : "p-4 border-border/50 bg-card/50 opacity-80 hover:opacity-100"
                  )}>
                    
                    <div className={isCurrent ? "p-4 space-y-4" : "space-y-3"}>
                      {ms.tasks && ms.tasks.map((task, tIdx) => {
                        const taskId = `ms${index}-t${tIdx}`;
                        const isChecked = isCompleted || checkedTasks[taskId];
                        return (
                          <div key={tIdx} className="flex items-start gap-3">
                            {isCompleted ? (
                               <Checkbox id={taskId} checked disabled className="mt-0.5 data-[state=checked]:bg-primary data-[state=checked]:border-primary" />
                            ) : !isCurrent ? (
                               <div className="size-4 rounded border border-muted-foreground/50 mt-0.5 shrink-0" />
                            ) : (
                               <Checkbox 
                                 id={taskId} 
                                 className="mt-0.5" 
                                 checked={isChecked}
                                 onCheckedChange={() => toggleTask(taskId)} 
                               />
                            )}
                            
                            <div className="flex-1">
                              {isCompleted ? (
                                <>
                                  <label className="text-sm font-medium line-through text-muted-foreground">{task}</label>
                                  {ms.topics && ms.topics[tIdx] && <p className="text-xs text-muted-foreground mt-0.5">{ms.topics[tIdx]}</p>}
                                </>
                              ) : !isCurrent ? (
                                <>
                                  <span className="text-sm font-medium text-foreground">{task}</span>
                                  {ms.topics && ms.topics[tIdx] && <p className="text-xs text-muted-foreground mt-0.5">{ms.topics[tIdx]}</p>}
                                </>
                              ) : (
                                <>
                                  <label htmlFor={taskId} className="text-sm font-medium text-foreground cursor-pointer">{task}</label>
                                  {ms.topics && ms.topics[tIdx] && <p className="text-xs text-muted-foreground mt-0.5">{ms.topics[tIdx]}</p>}
                                </>
                              )}
                            </div>
                          </div>
                        );
                      })}
                      
                      {/* Fallback if no tasks list provided */}
                      {(!ms.tasks || ms.tasks.length === 0) && ms.topics && ms.topics.map((topic, tIdx) => (
                          <div key={tIdx} className="flex items-start gap-3">
                            <div className="size-4 rounded border border-muted-foreground/50 mt-0.5 shrink-0" />
                            <div className="flex-1"><span className="text-sm font-medium text-foreground">{topic}</span></div>
                          </div>
                      ))}
                    </div>

                    {/* Resources section */}
                    {ms.resources && ms.resources.length > 0 && (
                      <div className={cn(
                        "flex flex-col gap-2",
                        isCurrent ? "bg-secondary/30 p-3 border-t border-border/50" : "mt-4 pt-3 border-t border-border/50"
                      )}>
                        {isCurrent && <p className="text-[10px] uppercase tracking-wider font-medium text-muted-foreground mb-1">Curated Resources</p>}
                        
                        {ms.resources.map((res, rIdx) => {
                          const Icon = res.resource_type?.toLowerCase().includes("video") || res.resource_type?.toLowerCase().includes("course") ? PlayCircle : BookOpen;
                          
                          if (isCurrent) {
                            return (
                              <a key={rIdx} href={res.url || "#"} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 p-2 rounded-md hover:bg-background transition-colors group/link border border-transparent hover:border-border/50 shadow-sm">
                                <Icon className="size-4 text-primary shrink-0" />
                                <span className="text-xs font-medium truncate flex-1">{res.title}</span>
                                {res.provider && <span className="text-[10px] text-muted-foreground whitespace-nowrap">{res.provider}</span>}
                              </a>
                            );
                          } else {
                            return (
                              <div key={rIdx} className="flex items-center gap-2 text-xs text-muted-foreground">
                                <Icon className="size-3 shrink-0" />
                                <span className="truncate">{res.title}</span>
                              </div>
                            );
                          }
                        })}
                      </div>
                    )}
                  </Card>
                </div>

              </div>
            );
          })}
        </div>

        <div className="mt-16 flex justify-center">
          <Button variant="secondary" className="px-8 shadow-sm" onClick={() => navigate("/report")}>
            Finish & View Report
          </Button>
        </div>

      </div>
    </AppShell>
  );
}
