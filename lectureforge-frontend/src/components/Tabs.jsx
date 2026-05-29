import React from "react";

const tabs = [
  { id: "outline", label: "Outline" },
  { id: "summaries", label: "Summary" },
  { id: "mind-map", label: "Mind Map" },
  { id: "flashcards", label: "Flashcards" },
  { id: "search", label: "Search" },
];

export default function Tabs({ activeTab, setActiveTab }) {
  return (
    <nav className="flex items-end gap-8 overflow-x-auto">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => setActiveTab(tab.id)}
          className={`whitespace-nowrap border-b-2 pb-2 pt-2 font-serif text-base transition ${
            activeTab === tab.id
              ? "border-[var(--app-accent)] text-[var(--app-text)]"
              : "border-transparent text-[var(--app-muted)] hover:text-[var(--app-text)]"
          }`}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
}
