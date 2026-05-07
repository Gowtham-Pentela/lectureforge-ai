import React from "react";
const tabs = [
  { id: "outline", label: "Outline" },
  { id: "summaries", label: "Summaries" },
  { id: "flashcards", label: "Flashcards" },
  { id: "concept-map", label: "Concept Map" },
  { id: "search", label: "Search" },
  { id: "transcript", label: "Transcript" },
];

export default function Tabs({ activeTab, setActiveTab }) {
  return (
    <div className="mb-5 flex gap-2 overflow-x-auto rounded-2xl border border-slate-200 bg-white p-2 shadow-sm">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => setActiveTab(tab.id)}
          className={`whitespace-nowrap rounded-xl px-4 py-2 text-sm font-semibold transition ${
            activeTab === tab.id
              ? "bg-blue-600 text-white shadow-md shadow-blue-600/20"
              : "text-slate-600 hover:bg-slate-100"
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
