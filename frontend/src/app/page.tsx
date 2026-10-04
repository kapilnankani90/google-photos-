"use client";

import { useState } from "react";
import MemorySearch from "./MemorySearch";
import DiscoveryEngineConsole from "./DiscoveryEngineConsole";
import { Sparkles, Terminal } from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"memory-search" | "evaluator">("memory-search");

  return (
    <main className="container">
      {/* Universal Google Photos Brand Navigation Header */}
      <header className="header">
        <div className="brand-section">
          <div className="brand-logo-pinwheel">
            <div className="pin-red" />
            <div className="pin-blue" />
            <div className="pin-yellow" />
            <div className="pin-green" />
          </div>
          <div>
            <h1 className="brand-title">Google Photos</h1>
            <p className="brand-subtitle">
              {activeTab === "memory-search"
                ? "Memory Search · AI-Native Consumer Prototype"
                : "Discovery Engine · Deliverable 1 Evaluator Console"}
            </p>
          </div>
        </div>

        {/* View Switcher / Tab Navigation */}
        <div className="view-switcher-bar">
          <button
            type="button"
            className={`view-switcher-btn ${activeTab === "memory-search" ? "active" : ""}`}
            onClick={() => setActiveTab("memory-search")}
            title="Switch to consumer-facing Memory Search MVP"
          >
            <Sparkles size={15} color={activeTab === "memory-search" ? "#FBBC05" : "#94A3B8"} />
            <span>Memory Search (MVP)</span>
          </button>

          <button
            type="button"
            className={`view-switcher-btn ${activeTab === "evaluator" ? "active" : ""}`}
            onClick={() => setActiveTab("evaluator")}
            title="Switch to technical Part 1 Discovery Engine Console"
          >
            <Terminal size={15} color={activeTab === "evaluator" ? "#60A5FA" : "#94A3B8"} />
            <span>Part 1 Evaluator Console</span>
          </button>
        </div>
      </header>

      {/* Main Experience View */}
      {activeTab === "memory-search" ? (
        <MemorySearch />
      ) : (
        <DiscoveryEngineConsole />
      )}
    </main>
  );
}
