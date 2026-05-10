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

export default function FacultyAuditDashboard({ audit }) {
  const [activeTab, setActiveTab] = useState("summary");

  if (!audit) {
    return null;
  }

  const highestImpactFix = audit.highest_impact_fix || {};
  const priorityFixes = audit.priority_fixes || [];
  const rewrites = audit.timestamped_rewrites || [];

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
    <section className="w-full max-w-6xl mx-auto mt-8">
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 mb-6">
        <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
          <div>
            <div className="flex items-center gap-2 text-indigo-600 mb-2">
              <ShieldCheck size={18} />
              <p className="text-sm font-semibold">Private Faculty Report</p>
            </div>

            <h2 className="text-2xl font-bold text-slate-900">
              Faculty Lecture Audit
            </h2>

            <p className="text-slate-600 mt-2 max-w-3xl leading-7">
              This report is private and intended only for the instructor. It is
              designed to support lecture improvement, not evaluate or monitor
              faculty performance.
            </p>

            {audit.lecture_title && (
              <p className="text-sm text-slate-500 mt-3">
                Lecture: {audit.lecture_title}
              </p>
            )}
          </div>

          <button
            onClick={downloadReport}
            className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-slate-900 text-white hover:bg-slate-800 transition"
          >
            <Download size={18} />
            Download Report
          </button>
        </div>
      </div>

      <div className="bg-indigo-50 border border-indigo-100 rounded-2xl p-5 mb-6">
        <div className="flex items-center gap-2 text-indigo-700 mb-2">
          <Lightbulb size={18} />
          <p className="text-sm font-semibold">
            If you change one thing before publishing, change this:
          </p>
        </div>

        <div className="space-y-2">
          <p className="text-sm text-slate-500">
            Timestamp: {highestImpactFix.timestamp || "N/A"}
          </p>

          <p className="text-slate-800">
            <strong>Issue:</strong>{" "}
            {highestImpactFix.issue || "No issue identified."}
          </p>

          <p className="text-slate-700">
            <strong>Why it matters:</strong>{" "}
            {highestImpactFix.why_it_matters || "No explanation available."}
          </p>

          <p className="text-slate-700">
            <strong>Suggested improvement:</strong>{" "}
            {highestImpactFix.suggested_improvement ||
              "No suggested improvement available."}
          </p>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-6">
        {tabs.map((tab) => {
          const Icon = tab.icon;

          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl border text-sm transition ${
                activeTab === tab.id
                  ? "bg-slate-900 text-white border-slate-900"
                  : "bg-white text-slate-700 border-slate-200 hover:bg-slate-50"
              }`}
            >
              <Icon size={16} />
              {tab.label}
            </button>
          );
        })}
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
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
            <h3 className="text-xl font-semibold text-slate-900 mb-4">
              Priority Fix List
            </h3>

            {priorityFixes.length === 0 ? (
              <EmptyState message="No priority fixes were returned." />
            ) : (
              <div className="space-y-4">
                {priorityFixes.map((fix, index) => (
                  <div
                    key={`${fix.timestamp}-${index}`}
                    className="border border-slate-200 rounded-xl p-4"
                  >
                    <div className="flex items-center justify-between gap-4 mb-3">
                      <span className="font-semibold text-slate-900">
                        {index + 1}. {fix.priority} Priority
                      </span>

                      <span className="text-sm text-slate-500">
                        {fix.timestamp}
                      </span>
                    </div>

                    <p className="text-slate-800 font-medium">{fix.issue}</p>

                    <p className="text-slate-600 mt-3">
                      <strong>Why it matters:</strong> {fix.why_it_matters}
                    </p>

                    <p className="text-slate-600 mt-3">
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
            <h3 className="text-xl font-semibold text-slate-900 mb-4">
              Timestamped Suggested Rewrites
            </h3>

            {rewrites.length === 0 ? (
              <EmptyState message="No timestamped rewrites were returned." />
            ) : (
              <div className="space-y-4">
                {rewrites.map((rewrite, index) => (
                  <div
                    key={`${rewrite.timestamp}-${index}`}
                    className="border border-slate-200 rounded-xl p-4"
                  >
                    <div className="text-sm font-semibold text-indigo-600 mb-3">
                      {rewrite.timestamp}
                    </div>

                    <p className="text-slate-700">
                      <strong>Current issue:</strong>{" "}
                      {rewrite.current_issue}
                    </p>

                    <p className="text-slate-700 mt-3">
                      <strong>Suggested rewrite:</strong>{" "}
                      {rewrite.suggested_rewrite}
                    </p>

                    <p className="text-slate-600 mt-3">
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
    </section>
  );
}

function TextBlock({ title, content }) {
  return (
    <div>
      <h3 className="text-xl font-semibold text-slate-900 mb-3">{title}</h3>
      <p className="text-slate-700 leading-7">
        {content || "Insufficient evidence available."}
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
      <div className="flex items-center gap-2 mb-3">
        <Icon size={20} className="text-indigo-600" />
        <h3 className="text-xl font-semibold text-slate-900">{title}</h3>
      </div>

      <p className="text-slate-700 leading-7 mb-5">
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
    <div className="border border-slate-200 rounded-xl p-4">
      <h4 className="font-semibold text-slate-900 mb-3">{title}</h4>

      {items.length === 0 ? (
        <p className="text-sm text-slate-500">No specific items returned.</p>
      ) : (
        <ul className="space-y-2">
          {items.map((item, index) => (
            <li key={index} className="text-slate-700 text-sm leading-6">
              • {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function EmptyState({ message }) {
  return (
    <div className="border border-dashed border-slate-300 rounded-xl p-6 text-center text-slate-500">
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