import React, { useState } from "react";
import {
  AlertCircle,
  BookOpen,
  Brain,
  Captions,
  Clock,
  Download,
  Lightbulb,
  MessageSquare,
  ShieldCheck,
  Users,
} from "lucide-react";
import { buildYouTubeEmbedUrl } from "../lib/youtube";

export default function FacultyAuditDashboard({ audit, sourceVideoUrl }) {
  const [activeTab, setActiveTab] = useState("summary");

  if (!audit) {
    return null;
  }

  const highestImpactFix = audit.highest_impact_fix || {};
  const priorityFixes = audit.priority_fixes || [];
  const rewrites = audit.timestamped_rewrites || [];
  const embedUrl = buildYouTubeEmbedUrl(sourceVideoUrl);
  const dimensions = [
    audit.pedagogical_clarity,
    audit.accessibility,
    audit.equity_and_inclusion,
    audit.structure_and_pacing,
    audit.cognitive_load,
    audit.student_engagement,
  ].filter(Boolean);

  const downloadReport = () => {
    const reportText = buildMarkdownReport(audit);
    const blob = new Blob([reportText], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);

    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "faculty_lecture_audit.md";
    anchor.click();

    URL.revokeObjectURL(url);
  };

  const tabs = [
    {
      id: "summary",
      label: "Summary",
      icon: BookOpen,
    },
    {
      id: "fixes",
      label: "Priority Fixes",
      icon: AlertCircle,
    },
    {
      id: "accessibility",
      label: "Accessibility",
      icon: Captions,
    },
    {
      id: "equity",
      label: "Equity & Clarity",
      icon: Users,
    },
    {
      id: "pacing",
      label: "Pacing & Load",
      icon: Clock,
    },
    {
      id: "rewrites",
      label: "Rewrites",
      icon: MessageSquare,
    },
  ];

  return (
    <main className="-mx-4 -mb-6 border-t border-[var(--app-border)] sm:-mx-6">
      <section className="grid min-h-[calc(100vh-4rem)] lg:grid-cols-[50%_50%]">
        <div className="border-b border-[var(--app-border)] bg-[var(--app-panel)] px-4 py-5 sm:px-6 lg:border-b-0 lg:border-r">
          <div className="mb-5 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="mb-2 text-xs font-bold uppercase tracking-[0.24em] text-[var(--app-soft)]">
                Faculty review
              </p>

              <h1 className="max-w-4xl font-serif text-3xl font-semibold leading-tight text-[var(--app-text)]">
                {audit.lecture_title || "Faculty Lecture Audit"}
              </h1>

              <div className="mt-3 flex flex-wrap gap-4 text-sm font-semibold text-[var(--app-muted)]">
                <span className="inline-flex items-center gap-1.5">
                  <ShieldCheck className="h-4 w-4" />
                  Private report
                </span>
                <span>{priorityFixes.length} priority fixes</span>
                <span>{rewrites.length} rewrites</span>
                <span>{dimensions.length} dimensions</span>
              </div>
            </div>

            <button
              onClick={downloadReport}
              className="inline-flex shrink-0 items-center justify-center gap-2 rounded-md bg-[var(--app-accent)] px-4 py-2 text-sm font-black text-white shadow-[0_12px_28px_rgba(41,53,232,0.24)] transition hover:-translate-y-0.5"
            >
              <Download size={17} />
              Download
            </button>
          </div>

          <div className="overflow-hidden rounded-md border border-[var(--app-border)] bg-black shadow-[0_18px_45px_rgba(15,23,42,0.16)]">
            {embedUrl ? (
              <iframe
                title={audit.lecture_title || "Lecture video"}
                src={embedUrl}
                className="aspect-video w-full"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowFullScreen
              />
            ) : (
              <div className="grid aspect-video place-items-center bg-slate-950 px-6 text-center text-sm text-white">
                Video preview is available after a valid YouTube URL is
                processed.
              </div>
            )}
          </div>

          <div className="mt-5 border-l-2 border-[var(--app-red)] bg-[var(--app-red-soft)] px-5 py-4">
            <div className="mb-3 flex items-center gap-2 text-[var(--app-red)]">
              <Lightbulb size={18} />
              <p className="text-xs font-black uppercase tracking-[0.2em]">
                Highest impact fix
              </p>
            </div>

            <div className="space-y-3 text-sm leading-6 text-[var(--app-text)]">
              <p className="font-mono text-xs font-bold text-[var(--app-red)]">
                {highestImpactFix.timestamp || "N/A"}
              </p>
              <p className="text-lg font-semibold">
                {highestImpactFix.issue || "No issue identified."}
              </p>
              <p className="text-[var(--app-muted)]">
                {highestImpactFix.why_it_matters ||
                  "No explanation available."}
              </p>
              <p>
                {highestImpactFix.suggested_improvement ||
                  "No suggested improvement available."}
              </p>
            </div>
          </div>

          <div className="mt-5">
            <p className="mb-3 text-xs font-bold uppercase tracking-[0.24em] text-[var(--app-soft)]">
              Review snapshot
            </p>
            <div className="grid gap-3 sm:grid-cols-3">
              <Metric label="Fixes" value={priorityFixes.length} />
              <Metric label="Rewrites" value={rewrites.length} />
              <Metric label="Areas" value={dimensions.length} />
            </div>
          </div>
        </div>

        <aside className="bg-[var(--app-panel-muted)]">
          <div className="flex min-h-16 flex-col gap-3 border-b border-[var(--app-border)] px-5 py-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex flex-wrap gap-1">
              {tabs.map((tab) => {
                const Icon = tab.icon;

                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`inline-flex items-center gap-2 border-b-2 px-3 py-2 text-sm font-semibold transition ${
                      activeTab === tab.id
                        ? "border-[var(--app-red)] text-[var(--app-text)]"
                        : "border-transparent text-[var(--app-muted)] hover:text-[var(--app-text)]"
                    }`}
                  >
                    <Icon size={16} />
                    {tab.label}
                  </button>
                );
              })}
            </div>

            <div className="rounded-md border border-[var(--app-border)] bg-[var(--app-panel)] px-3 py-2 text-xs font-bold uppercase tracking-[0.18em] text-[var(--app-soft)]">
              Instructor only
            </div>
          </div>

          <div className="h-[calc(100vh-8rem)] overflow-y-auto px-5 py-5">
            {activeTab === "summary" && (
              <div className="space-y-8">
                <TextBlock
                  title="Overall Summary"
                  content={audit.overall_summary}
                />

                <TextBlock title="Final Notes" content={audit.final_notes} />
              </div>
            )}

            {activeTab === "fixes" && (
              <div>
                <h3 className="mb-4 font-serif text-2xl font-semibold text-[var(--app-text)]">
                  Priority Fix List
                </h3>

                {priorityFixes.length === 0 ? (
                  <EmptyState message="No priority fixes were returned." />
                ) : (
                  <div className="space-y-4">
                    {priorityFixes.map((fix, index) => (
                      <div
                        key={`${fix.timestamp}-${index}`}
                        className="border border-[var(--app-border)] bg-[var(--app-panel)] p-4"
                      >
                        <div className="mb-3 flex items-center justify-between gap-4">
                          <span className="font-semibold text-[var(--app-text)]">
                            {index + 1}. {fix.priority} Priority
                          </span>

                          <span className="font-mono text-sm text-[var(--app-accent)]">
                            {fix.timestamp}
                          </span>
                        </div>

                        <p className="font-medium text-[var(--app-text)]">
                          {fix.issue}
                        </p>

                        <p className="mt-3 text-[var(--app-muted)]">
                          <strong>Why it matters:</strong> {fix.why_it_matters}
                        </p>

                        <p className="mt-3 text-[var(--app-muted)]">
                          <strong>Suggested improvement:</strong>{" "}
                          {fix.suggested_improvement}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === "accessibility" && (
              <DimensionSection
                title="Accessibility"
                icon={Captions}
                dimension={audit.accessibility}
              />
            )}

            {activeTab === "equity" && (
              <div className="space-y-8">
                <DimensionSection
                  title="Equity and Inclusion"
                  icon={Users}
                  dimension={audit.equity_and_inclusion}
                />

                <DimensionSection
                  title="Pedagogical Clarity"
                  icon={BookOpen}
                  dimension={audit.pedagogical_clarity}
                />
              </div>
            )}

            {activeTab === "pacing" && (
              <div className="space-y-8">
                <DimensionSection
                  title="Structure and Pacing"
                  icon={Clock}
                  dimension={audit.structure_and_pacing}
                />

                <DimensionSection
                  title="Cognitive Load"
                  icon={Brain}
                  dimension={audit.cognitive_load}
                />

                <DimensionSection
                  title="Student Engagement"
                  icon={MessageSquare}
                  dimension={audit.student_engagement}
                />
              </div>
            )}

            {activeTab === "rewrites" && (
              <div>
                <h3 className="mb-4 font-serif text-2xl font-semibold text-[var(--app-text)]">
                  Timestamped Suggested Rewrites
                </h3>

                {rewrites.length === 0 ? (
                  <EmptyState message="No timestamped rewrites were returned." />
                ) : (
                  <div className="space-y-4">
                    {rewrites.map((rewrite, index) => (
                      <div
                        key={`${rewrite.timestamp}-${index}`}
                        className="border border-[var(--app-border)] bg-[var(--app-panel)] p-4"
                      >
                        <div className="mb-3 font-mono text-sm font-semibold text-[var(--app-accent)]">
                          {rewrite.timestamp}
                        </div>

                        <p className="text-[var(--app-text)]">
                          <strong>Current issue:</strong>{" "}
                          {rewrite.current_issue}
                        </p>

                        <p className="mt-3 text-[var(--app-text)]">
                          <strong>Suggested rewrite:</strong>{" "}
                          {rewrite.suggested_rewrite}
                        </p>

                        <p className="mt-3 text-[var(--app-muted)]">
                          <strong>Why this helps:</strong>{" "}
                          {rewrite.why_this_helps}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </aside>
      </section>
    </main>
  );
}

function TextBlock({ title, content }) {
  return (
    <div>
      <h3 className="mb-3 font-serif text-2xl font-semibold text-[var(--app-text)]">
        {title}
      </h3>
      <p className="leading-7 text-[var(--app-text)]">
        {content || "Insufficient evidence available."}
      </p>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="border border-[var(--app-border)] bg-[var(--app-panel-muted)] px-4 py-3">
      <p className="font-mono text-2xl font-black text-[var(--app-text)]">
        {value}
      </p>
      <p className="mt-1 text-xs font-bold uppercase tracking-[0.18em] text-[var(--app-soft)]">
        {label}
      </p>
    </div>
  );
}

function DimensionSection({ title, icon: Icon, dimension }) {
  const data = dimension || {
    summary: "Insufficient evidence available.",
    strengths: [],
    opportunities: [],
  };

  return (
    <div>
      <div className="mb-3 flex items-center gap-2">
        <Icon size={20} className="text-[var(--app-accent)]" />
        <h3 className="font-serif text-2xl font-semibold text-[var(--app-text)]">
          {title}
        </h3>
      </div>

      <p className="mb-5 leading-7 text-[var(--app-text)]">
        {data.summary || "Insufficient evidence available."}
      </p>

      <div className="grid gap-4 md:grid-cols-2">
        <ListCard title="What is working" items={data.strengths || []} />
        <ListCard
          title="Improvement opportunities"
          items={data.opportunities || []}
        />
      </div>
    </div>
  );
}

function ListCard({ title, items }) {
  return (
    <div className="border border-[var(--app-border)] bg-[var(--app-panel)] p-4">
      <h4 className="mb-3 font-semibold text-[var(--app-text)]">{title}</h4>

      {items.length === 0 ? (
        <p className="text-sm text-[var(--app-muted)]">
          No specific items returned.
        </p>
      ) : (
        <ul className="space-y-2">
          {items.map((item, index) => (
            <li
              key={index}
              className="grid grid-cols-[1rem_1fr] gap-2 text-sm leading-6 text-[var(--app-text)]"
            >
              <span className="text-[var(--app-red)]">-</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function EmptyState({ message }) {
  return (
    <div className="border border-dashed border-[var(--app-border)] bg-[var(--app-panel)] p-6 text-center text-[var(--app-muted)]">
      {message}
    </div>
  );
}

function buildMarkdownReport(audit) {
  const highestImpactFix = audit.highest_impact_fix || {};
  const priorityFixes = audit.priority_fixes || [];
  const rewrites = audit.timestamped_rewrites || [];

  return `
# Faculty Lecture Audit Report

## Lecture Title
${audit.lecture_title || "Untitled Lecture"}

## Private Use Note
This report is private and intended only for the instructor. It is designed to support lecture improvement, not evaluate or monitor faculty performance.

## Overall Summary
${audit.overall_summary || "Insufficient evidence available."}

## Highest Impact Fix
Timestamp: ${highestImpactFix.timestamp || "N/A"}

Issue:
${highestImpactFix.issue || "No issue identified."}

Why it matters:
${highestImpactFix.why_it_matters || "No explanation available."}

Suggested improvement:
${highestImpactFix.suggested_improvement || "No suggested improvement available."}

## Priority Fix List
${priorityFixes
  .map(
    (fix, index) => `
${index + 1}. ${fix.priority} Priority

Timestamp: ${fix.timestamp}

Issue:
${fix.issue}

Why it matters:
${fix.why_it_matters}

Suggested improvement:
${fix.suggested_improvement}
`
  )
  .join("\n")}

## Pedagogical Clarity
${formatDimensionForMarkdown(audit.pedagogical_clarity)}

## Accessibility
${formatDimensionForMarkdown(audit.accessibility)}

## Equity and Inclusion
${formatDimensionForMarkdown(audit.equity_and_inclusion)}

## Structure and Pacing
${formatDimensionForMarkdown(audit.structure_and_pacing)}

## Cognitive Load
${formatDimensionForMarkdown(audit.cognitive_load)}

## Student Engagement
${formatDimensionForMarkdown(audit.student_engagement)}

## Timestamped Suggested Rewrites
${rewrites
  .map(
    (rewrite) => `
### ${rewrite.timestamp}

Current issue:
${rewrite.current_issue}

Suggested rewrite:
${rewrite.suggested_rewrite}

Why this helps:
${rewrite.why_this_helps}
`
  )
  .join("\n")}

## Final Notes
${audit.final_notes || ""}
`;
}

function formatDimensionForMarkdown(dimension) {
  if (!dimension) {
    return "Insufficient evidence available.";
  }

  const strengths = dimension.strengths || [];
  const opportunities = dimension.opportunities || [];

  return `
Summary:
${dimension.summary || "Insufficient evidence available."}

What is working:
${
  strengths.map((item) => `- ${item}`).join("\n") ||
  "- No specific items returned."
}

Improvement opportunities:
${
  opportunities.map((item) => `- ${item}`).join("\n") ||
  "- No specific items returned."
}
`;
}
