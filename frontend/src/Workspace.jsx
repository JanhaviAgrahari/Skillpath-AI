import React, { useState, useEffect, useRef } from "react";
import { AppShell } from "./_shared/AppShell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { BrainCircuit, CheckCircle2, Sparkles, Send, Loader2 } from "lucide-react";

export function Workspace() {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  
  // Right side panel state
  const [skills, setSkills] = useState([]);
  const [assessedSkills, setAssessedSkills] = useState({});
  const [progressData, setProgressData] = useState({ answered_questions: 0, total_questions: 10 });
  const [assessmentComplete, setAssessmentComplete] = useState(false);

  const scrollRef = useRef(null);

  useEffect(() => {
    // Scroll to bottom every time messages change
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  useEffect(() => {
    const initAssessment = async () => {
      const storedSessionId = localStorage.getItem("session_id");
      if (!storedSessionId) {
         window.location.href = "/";
         return;
      }
      setSessionId(storedSessionId);

      setIsTyping(true);
      try {
        // 1. Check if assessment is already active or we need to start it
        let assessData;
        try {
          const fetchRes = await fetch(`http://localhost:8000/api/v1/sessions/${storedSessionId}/assessment`);
          if (fetchRes.ok) {
            assessData = await fetchRes.json();
          } else {
            assessData = { success: false };
          }
        } catch (e) {
          // endpoint might 404 if not started
          assessData = { success: false };
        }

        let currentActiveQuestion = null;
        let runningProgress = { answered_questions: 0, total_questions: 10 };

        if (!assessData.success || !assessData.data?.current_question) {
           // We need to get analysis to know what skills to assess
           const analysisRes = await fetch(`http://localhost:8000/api/v1/sessions/${storedSessionId}/analysis/complete`);
           const analysisData = analysisRes.ok ? await analysisRes.json() : { success: false };
           
           let recommendedSkills = [];
           if (analysisData.success && analysisData.data) {
             // Try to get skills from analysis result first, then fall back to JD snapshot
             const result = analysisData.data.result || {};
             const jdSkills = (result.jd_skills || []).map(s => s.canonical_name || s.name || s);
             const assessmentRecs = result.assessment_recommendations || [];
             
             if (assessmentRecs.length > 0) {
               recommendedSkills = assessmentRecs;
             } else if (jdSkills.length > 0) {
               recommendedSkills = jdSkills;
             } else {
               // Fall back to JD snapshot raw lists
               const jd = analysisData.data.jd_snapshot || {};
               const allJD = [...(jd.required_skills || []), ...(jd.preferred_skills || [])];
               recommendedSkills = allJD.length > 0 ? allJD.map(s => s.name || s) : [];
             }
             setSkills(recommendedSkills.slice(0, 8));
           }
           
           if (recommendedSkills.length === 0) {
             recommendedSkills = ["SQL", "Python", "Problem Solving"];
             setSkills(recommendedSkills);
           }
           
           // Start assessment
           const startRes = await fetch(`http://localhost:8000/api/v1/sessions/${storedSessionId}/assessment/start`, {
             method: "POST",
             headers: { "Content-Type": "application/json" },
             body: JSON.stringify({
               skills_to_assess: recommendedSkills,
               questions_per_skill: 1,
               expected_level: "intermediate"
             })
           });
           const startData = await startRes.json();
           if (startData.success && startData.data) {
             currentActiveQuestion = startData.data.current_question;
             if (startData.data.progress) runningProgress = startData.data.progress;
           }
        } else {
           currentActiveQuestion = assessData.data.current_question;
           if (assessData.data.progress) runningProgress = assessData.data.progress;
           // Fetch analysis to populate skills in the UI sidebar
           const analysisRes = await fetch(`http://localhost:8000/api/v1/sessions/${storedSessionId}/analysis/complete`);
           const analysisData = analysisRes.ok ? await analysisRes.json() : { success: false };
           if (analysisData.success && analysisData.data) {
               const result = analysisData.data.result || {};
               const jdSkills = (result.jd_skills || []).map(s => s.canonical_name || s.name || s);
               const assessmentRecs = result.assessment_recommendations || [];
               const skillsList = assessmentRecs.length > 0 ? assessmentRecs : jdSkills;
               setSkills(skillsList.length > 0 ? skillsList.slice(0, 8) : ["SQL", "Python", "Problem Solving"]);
           } else {
               setSkills(["SQL", "Python", "Problem Solving"]);
           }
        }
        
        setProgressData(runningProgress);

        if (currentActiveQuestion) {
          setCurrentQuestion(currentActiveQuestion);
          setMessages([
            { id: Date.now(), role: "agent", type: "question", text: currentActiveQuestion.question_text, context: currentActiveQuestion.context }
          ]);
        }
        
      } catch (err) {
        console.error("Failed to init assessment", err);
      } finally {
        setIsTyping(false);
      }
    };

    initAssessment();
  }, []);

  const handleSend = async (textToSend) => {
    const text = textToSend || inputValue;
    if (!text.trim() || isTyping || !currentQuestion || assessmentComplete) return;

    // Add user message
    const newMsg = { id: Date.now(), role: "user", text: text };
    setMessages(prev => [...prev, newMsg]);
    setInputValue("");
    setIsTyping(true);

    try {
      const res = await fetch(`http://localhost:8000/api/v1/sessions/${sessionId}/assessment/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question_id: currentQuestion.question_id || currentQuestion.id,
          answer_text: text
        })
      });
      const data = await res.json();
      
      if (!data.success) throw new Error(data.error_message || "Failed");

      const { evaluation, skill_score, skill_proficiency, next_question, progress } = data.data;

      // Update right panel skills dictionary using the current question's skill
      const answeredSkill = currentQuestion?.skill_name || currentQuestion?.skill || "General";
      setAssessedSkills(prev => ({
         ...prev,
         [answeredSkill]: { score: skill_score, proficiency: skill_proficiency }
      }));

      // Add evaluation message
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: "agent",
        type: "evaluation",
        score: skill_score,
        skill: answeredSkill,
        text: evaluation?.feedback || "Great.",
        nextIntro: next_question ? (next_question.is_follow_up ? "Let's dig a bit deeper into your previous response." : "Moving on to the next question.") : null
      }]);

      if (progress) setProgressData(progress);

      if (next_question) {
        setCurrentQuestion(next_question);
        // We delay the next question appearance slightly to simulate thinking
        setTimeout(() => {
          setMessages(prev => [...prev, {
            id: Date.now() + 2,
            role: "agent",
            type: "question",
            text: next_question.question_text,
            context: next_question.context
          }]);
          setIsTyping(false);
        }, 1000);
      } else {
        // Assessment Complete
        setAssessmentComplete(true);
        setIsTyping(false);

        await fetch(`http://localhost:8000/api/v1/sessions/${sessionId}/assessment/complete`, {
           method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({})
        });

        // Add final message
        setMessages(prev => [...prev, {
          id: Date.now() + 3,
          role: "agent",
          type: "system",
          text: "Assessment is complete. Let's move on to the learning plan."
        }]);
      }
    } catch (err) {
      console.error(err);
      setIsTyping(false);
      setMessages(prev => [...prev, {
         id: Date.now() + 1,
         role: "agent",
         type: "system",
         text: "Encountered an error. " + err.message
      }]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const currentSkillName = currentQuestion?.skill_name || currentQuestion?.skill || "General";
  const progressPercentage = progressData.total_questions > 0 ? (progressData.answered_questions / progressData.total_questions) * 100 : 0;

  return (
    <AppShell currentStage="assess">
      <div className="flex h-full w-full bg-background overflow-hidden relative">
        
        {/* LEFT COLUMN: Chat */}
        <div className="flex-1 flex flex-col min-w-0 border-r border-border/50 relative">
          <div className="h-14 flex items-center px-6 border-b border-border/50 bg-background/95 backdrop-blur z-10 shrink-0">
            <h2 className="text-sm font-medium text-foreground flex items-center gap-2">
              <BrainCircuit className="size-4 text-primary" />
              Assessment Session
            </h2>
          </div>

          <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-6 pb-40 scroll-smooth">
            <div className="text-center text-xs text-muted-foreground my-4">
              Agent started assessment • Setup Connected
            </div>

            {messages.map((msg) => {
              if (msg.role === "user") {
                return (
                  <div key={msg.id} className="flex gap-4 max-w-2xl ml-auto flex-row-reverse">
                    <div className="size-8 rounded-full bg-foreground text-background flex items-center justify-center shrink-0 mt-1 text-xs font-medium">
                      CU
                    </div>
                    <div className="space-y-2">
                      <div className="bg-foreground text-background rounded-2xl rounded-tr-sm p-4 text-sm leading-relaxed whitespace-pre-wrap">
                        {msg.text}
                      </div>
                    </div>
                  </div>
                );
              }

              if (msg.role === "agent") {
                if (msg.type === "evaluation") {
                  return (
                    <div key={msg.id} className="flex gap-4 max-w-2xl">
                      <div className="size-8 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center shrink-0 mt-1">
                        <BrainCircuit className="size-4 text-primary" />
                      </div>
                      <div className="space-y-2">
                        {msg.score !== undefined && (
                           <div className="flex items-center gap-2 mb-1">
                            <span className="inline-flex items-center gap-1 text-[10px] uppercase tracking-wider font-medium text-primary bg-primary/10 px-2 py-0.5 rounded-full">
                              <CheckCircle2 className="size-3" /> Score: {msg.score}/10
                            </span>
                            <span className="text-xs text-muted-foreground">{msg.skill} Proficiency</span>
                          </div>
                        )}
                        <div className="bg-secondary/30 border border-border/50 rounded-2xl rounded-tl-sm p-4 text-sm leading-relaxed text-foreground whitespace-pre-wrap">
                          <p>{msg.text}</p>
                          {msg.nextIntro && <p className="mt-3 font-medium">{msg.nextIntro}</p>}
                        </div>
                      </div>
                    </div>
                  );
                }
                if (msg.type === "system") {
                    return (
                      <div key={msg.id} className="flex justify-center max-w-2xl mx-auto">
                        <div className="text-xs font-medium bg-primary/10 text-primary px-3 py-1.5 rounded-full border border-primary/20">
                          {msg.text}
                        </div>
                      </div>
                    );
                }

                // Question
                return (
                  <div key={msg.id} className="flex gap-4 max-w-2xl">
                    <div className="size-8 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center shrink-0 mt-1">
                      <BrainCircuit className="size-4 text-primary" />
                    </div>
                    <div className="space-y-2">
                      <div className="bg-secondary/30 border border-border/50 rounded-2xl rounded-tl-sm p-4 text-sm leading-relaxed text-foreground whitespace-pre-wrap">
                       {msg.context && <p className="mb-2 italic text-muted-foreground/80">{msg.context}</p>}
                       <p>{msg.text}</p>
                      </div>
                    </div>
                  </div>
                );
              }
              return null;
            })}

            {/* Agent Thinking State */}
            {isTyping && (
              <div className="flex gap-4 max-w-2xl">
                <div className="size-8 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center shrink-0 mt-1">
                  <BrainCircuit className="size-4 text-primary" />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 mb-1 opacity-70">
                    <span className="inline-flex items-center gap-1.5 text-xs text-muted-foreground border border-border/50 bg-background px-2 py-1 rounded-md shadow-xs">
                      <span className="flex gap-0.5">
                        <span className="size-1 rounded-full bg-primary/60 animate-bounce" style={{ animationDelay: '0ms' }} />
                        <span className="size-1 rounded-full bg-primary/60 animate-bounce" style={{ animationDelay: '150ms' }} />
                        <span className="size-1 rounded-full bg-primary/60 animate-bounce" style={{ animationDelay: '300ms' }} />
                      </span>
                      Thinking...
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-background via-background to-transparent pt-10 pb-6 px-6 z-20">
            <div className="max-w-3xl mx-auto space-y-3">
              {!assessmentComplete && (
                <>
                  <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-none">
                    <button 
                      onClick={() => handleSend("I've used it for a few years.")}
                      className="shrink-0 inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full border border-border/60 bg-card hover:bg-secondary/50 transition-colors text-muted-foreground hover:text-foreground">
                      I've used it for a few years
                    </button>
                    <button 
                       onClick={() => handleSend("Mainly basic knowledge.")}
                       className="shrink-0 inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full border border-border/60 bg-card hover:bg-secondary/50 transition-colors text-muted-foreground hover:text-foreground">
                      Mainly basic knowledge
                    </button>
                    <button 
                       onClick={() => handleSend("I don't have experience with this.")}
                       className="shrink-0 inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full border border-border/60 bg-card hover:bg-secondary/50 transition-colors text-muted-foreground hover:text-foreground">
                      Skip this skill
                    </button>
                  </div>
                  <div className="relative flex items-end gap-2 bg-card border border-border shadow-sm rounded-xl p-2 focus-within:ring-1 focus-within:ring-primary/30 transition-all">
                    <textarea 
                      placeholder="Type your response..." 
                      className="w-full bg-transparent border-0 resize-none min-h-[44px] max-h-[120px] p-2 text-sm focus-visible:ring-0 focus-visible:outline-none scrollbar-none"
                      rows={1}
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyDown={handleKeyDown}
                      disabled={isTyping || assessmentComplete}
                    />
                    <Button 
                      size="icon" 
                      className="size-9 rounded-lg shrink-0 mb-0.5 bg-primary hover:bg-primary/90"
                      onClick={() => handleSend()}
                      disabled={!inputValue.trim() || isTyping}
                    >
                      {isTyping ? <Loader2 className="size-4 animate-spin text-primary-foreground" /> : <Send className="size-4 text-primary-foreground" />}
                    </Button>
                  </div>
                </>
              )}
              {assessmentComplete && (
                  <div className="flex justify-center mb-2">
                     <Button onClick={() => window.location.href = '/analyse'}>Continue to learning plan</Button>
                  </div>
              )}
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: Insights */}
        <div className="w-80 lg:w-96 shrink-0 bg-secondary/10 flex flex-col relative z-20">
          <div className="h-14 flex items-center px-6 border-b border-border/50 shrink-0">
            <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Live Insights</span>
          </div>

          <div className="flex-1 overflow-y-auto p-6 space-y-8">
            
            {/* Progress */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-foreground">Assessment Progress</span>
                <span className="text-xs font-medium text-primary">{progressData.answered_questions} / {progressData.total_questions} questions</span>
              </div>
              <Progress value={progressPercentage} className="h-1.5 bg-primary/10" />
            </div>

            {/* Why this question */}
            {currentQuestion && (
                <Card className="p-4 border-primary/20 bg-primary/5 shadow-none">
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="size-4 text-primary" />
                    <span className="text-sm font-medium text-foreground">Why this question?</span>
                  </div>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Assessing your proficiency in <strong>{currentSkillName}</strong> as part of the job requirements.
                  </p>
                </Card>
            )}

            {/* Extracted Skills */}
            <div>
              <h3 className="text-sm font-medium text-foreground mb-4">Extracted Requirements</h3>
              <div className="space-y-3">
                {skills.map((skillName, idx) => {
                  const assessment = assessedSkills[skillName];
                  const isCurrent = currentSkillName?.toLowerCase() === skillName.toLowerCase();
                  
                  if (assessment) {
                    return (
                      <div key={idx} className="flex items-center gap-3 opacity-80">
                        <CheckCircle2 className="size-4 text-emerald-500 shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium truncate">{skillName}</div>
                        </div>
                        <span className="text-xs font-medium text-emerald-600 bg-emerald-500/10 px-2 py-0.5 rounded">{assessment.score}/10</span>
                      </div>
                    );
                  }

                  if (isCurrent && !assessmentComplete) {
                     return (
                        <div key={idx} className="flex items-center gap-3 relative before:absolute before:left-[-12px] before:top-1/2 before:-translate-y-1/2 before:w-1 before:h-4 before:bg-primary before:rounded-full">
                          <div className="size-4 rounded-full border-2 border-primary border-t-transparent animate-spin shrink-0" />
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-medium text-primary truncate">{skillName}</div>
                          </div>
                          <span className="text-xs text-muted-foreground">Assessing...</span>
                        </div>
                     );
                  }

                  // Pending
                  return (
                    <div key={idx} className="flex items-center gap-3">
                      <div className="size-4 rounded-full border border-border shrink-0" />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm text-muted-foreground truncate">{skillName}</div>
                      </div>
                    </div>
                  );
                })}
                
                {skills.length === 0 && !isTyping && (
                  <p className="text-xs text-muted-foreground">No specific skills found or parsed.</p>
                )}

              </div>
            </div>

            <div className="pt-4 mt-4 border-t border-border/50">
               <Button variant="outline" className="w-full text-xs h-8" disabled={isTyping || assessmentComplete}>
                Pause Assessment
              </Button>
            </div>

          </div>
        </div>

      </div>
    </AppShell>
  );
}
