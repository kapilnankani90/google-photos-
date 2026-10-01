"use client";

import { useEffect, useState, useCallback } from "react";
import { 
  Activity, 
  Layers, 
  Cpu,
  AlertCircle
} from "lucide-react";

interface HealthData {
  status: string;
  service: string;
  version: string;
  environment: string;
  implementation_phase: string;
  components?: {
    database: string;
    embedding_model: string;
    gemini_api: string;
    evidence_corpus: string;
    subsystem_a: string;
    subsystem_b: string;
  };
}

export default function Home() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loadingHealth, setLoadingHealth] = useState<boolean>(true);
  const [backendError, setBackendError] = useState<string | null>(null);

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

  const fetchHealth = useCallback(async () => {
    setLoadingHealth(true);
    try {
      const res = await fetch(`${apiBaseUrl}/api/v1/health`);
      if (!res.ok) {
        throw new Error(`HTTP error ${res.status}`);
      }
      const data: HealthData = await res.json();
      setHealth(data);
      setBackendError(null);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to connect to backend";
      setBackendError(message);
      setHealth(null);
    } finally {
      setLoadingHealth(false);
    }
  }, [apiBaseUrl]);

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 8000);
    return () => clearInterval(interval);
  }, [fetchHealth]);

  return (
    <main className="container">
      {/* Header */}
      <header className="header">
        <div className="brand-section">
          <div className="brand-logo-pinwheel">
            <div className="pin-red" />
            <div className="pin-blue" />
            <div className="pin-yellow" />
            <div className="pin-green" />
          </div>
          <div>
            <h1 className="brand-title">Google Photos Discovery Engine</h1>
            <p className="brand-subtitle">Part 1 — Local Development Foundation (Step 1 of 13)</p>
          </div>
        </div>

        <div>
          {loadingHealth && !health ? (
            <span className="badge">
              <span className="pulse-dot" style={{ color: "#94A3B8" }} />
              Connecting to Backend...
            </span>
          ) : health ? (
            <span className="badge badge-connected">
              <span className="pulse-dot" />
              Backend Connected ({health.version})
            </span>
          ) : (
            <span className="badge badge-disconnected">
              <span className="pulse-dot" />
              Backend Offline ({apiBaseUrl})
            </span>
          )}
        </div>
      </header>

      {backendError && (
        <div style={{ 
          display: "flex", 
          alignItems: "center", 
          gap: "0.5rem", 
          padding: "0.75rem 1rem", 
          background: "rgba(234, 67, 53, 0.1)", 
          border: "1px solid rgba(234, 67, 53, 0.3)", 
          borderRadius: "8px", 
          marginBottom: "1.5rem",
          fontSize: "0.8125rem",
          color: "#F87171"
        }}>
          <AlertCircle size={16} />
          <span>Note: Backend API at {apiBaseUrl} is currently offline. Start the backend with <code>python -m uvicorn app.main:app --app-dir backend --port 8000</code>.</span>
        </div>
      )}

      {/* Main Grid: Runtime Status & Roadmap */}
      <div className="grid-2col">
        {/* Runtime Foundation Status */}
        <div className="card">
          <h2 className="card-title">
            <Activity size={18} color="#4285F4" />
            Runtime Foundation Status (Live)
          </h2>
          <p className="card-desc">
            Reported dynamically by FastAPI backend via <code style={{ color: "#93C5FD" }}>/api/v1/health</code>.
          </p>

          <div className="status-list">
            <div className="status-row">
              <span className="status-label">Implementation Phase</span>
              <span className="status-val" style={{ color: "#4ADE80" }}>
                {health?.implementation_phase || "Step 1 — Repository & Local Foundation"}
              </span>
            </div>
            <div className="status-row">
              <span className="status-label">Backend API Service</span>
              <span className="status-val">{health?.service || "FastAPI"}</span>
            </div>
            <div className="status-row">
              <span className="status-label">API Version</span>
              <span className="status-val">{health?.version || "0.1.0"}</span>
            </div>
            <div className="status-row">
              <span className="status-label">Environment</span>
              <span className="status-val">{health?.environment || "development"}</span>
            </div>
            <div className="status-row">
              <span className="status-label">Frontend Status</span>
              <span className="status-val" style={{ color: "#4ADE80" }}>Operational (Next.js 14 / React 18)</span>
            </div>
            <div className="status-row">
              <span className="status-label">Database Configuration</span>
              <span className="status-val" style={{ color: "#FBBF24" }}>
                Pending Step 2 (Supabase Foundation)
              </span>
            </div>
            <div className="status-row">
              <span className="status-label">Evidence Corpus</span>
              <span className="status-val" style={{ color: "#FBBF24" }}>
                308 cases/episodes — ingestion pending (Step 3)
              </span>
            </div>
            <div className="status-row">
              <span className="status-label">Embedding Model</span>
              <span className="status-val" style={{ color: "#FBBF24" }}>
                Pending benchmark (Step 5)
              </span>
            </div>
            <div className="status-row">
              <span className="status-label">Server-Side Gemini API</span>
              <span className="status-val" style={{ color: "#FBBF24" }}>
                Pending Step 7 (Grounded RAG)
              </span>
            </div>
          </div>

          <div className="callout">
            <div className="callout-title">Step 1 Foundation Guarantee</div>
            <p className="callout-text">
              Zero active database connections, zero external API keys, zero embedding models loaded, and zero fake results. All external dependencies are deferred strictly to their designated implementation steps.
            </p>
          </div>
        </div>

        {/* Subsystems & Sequential Roadmap */}
        <div className="card">
          <h2 className="card-title">
            <Layers size={18} color="#34A853" />
            Approved Part 1 Implementation Sequence
          </h2>
          <p className="card-desc">
            Sequential development stages governed by <code style={{ color: "#93C5FD" }}>part1_discovery_engine_implementation_spec.md</code>.
          </p>

          <div className="status-list">
            <div className="status-row">
              <span className="status-label">Step 1 — Repository &amp; Local Development Foundation</span>
              <span className="status-val" style={{ color: "#4ADE80" }}>Active / Current</span>
            </div>
            <div className="status-row">
              <span className="status-label">Step 2 — Supabase Foundation</span>
              <span className="status-val" style={{ color: "#94A3B8" }}>Pending</span>
            </div>
            <div className="status-row">
              <span className="status-label">Step 3 — Evidence Ingestion (308 cases)</span>
              <span className="status-val" style={{ color: "#94A3B8" }}>Pending</span>
            </div>
            <div className="status-row">
              <span className="status-label">Step 4 — V2 Representation Pipeline</span>
              <span className="status-val" style={{ color: "#94A3B8" }}>Pending</span>
            </div>
            <div className="status-row">
              <span className="status-label">Step 5 — Embedding Benchmark &amp; Model Selection</span>
              <span className="status-val" style={{ color: "#94A3B8" }}>Pending</span>
            </div>
            <div className="status-row">
              <span className="status-label">Step 6 — Multi-Path Retrieval &amp; Compositional Scoring</span>
              <span className="status-val" style={{ color: "#94A3B8" }}>Pending</span>
            </div>
            <div className="status-row">
              <span className="status-label">Step 7 — Grounded RAG &amp; Quote Validator</span>
              <span className="status-val" style={{ color: "#94A3B8" }}>Pending</span>
            </div>
            <div className="status-row">
              <span className="status-label">Step 8 — Complete FastAPI Backend</span>
              <span className="status-val" style={{ color: "#94A3B8" }}>Pending</span>
            </div>
            <div className="status-row">
              <span className="status-label">Step 9 — Research &amp; Evidence Console Frontend</span>
              <span className="status-val" style={{ color: "#94A3B8" }}>Pending</span>
            </div>
            <div className="status-row">
              <span className="status-label">Step 10 — Local End-to-End Validation</span>
              <span className="status-val" style={{ color: "#94A3B8" }}>Pending</span>
            </div>
            <div className="status-row">
              <span className="status-label">Steps 11–13 — Railway, Vercel &amp; Production Acceptance</span>
              <span className="status-val" style={{ color: "#94A3B8" }}>Pending</span>
            </div>
          </div>
        </div>
      </div>

      {/* Subsystems Architecture Notice */}
      <div className="card" style={{ marginTop: "1.5rem" }}>
        <h2 className="card-title">
          <Cpu size={18} color="#FBBC05" />
          Subsystem Architectural Boundaries
        </h2>
        <p className="card-desc">
          Part 1 operationalizes the strategic anchor across two distinct, complementary subsystems:
        </p>

        <div className="grid-2col" style={{ marginTop: "1rem" }}>
          <div style={{ padding: "1rem", background: "rgba(0,0,0,0.25)", borderRadius: "8px", border: "1px solid rgba(255,255,255,0.04)" }}>
            <h3 style={{ fontSize: "0.875rem", fontWeight: 700, color: "#93C5FD", marginBottom: "0.35rem" }}>
              Subsystem A: Algorithmic Discovery Core (Photo Retrieval)
            </h3>
            <p style={{ fontSize: "0.8125rem", color: "#94A3B8", lineHeight: 1.45 }}>
              7-stage deterministic retrieval pipeline (Stages 2–6) operating over photo media metadata. Implementation scheduled for Steps 4 and 6.
            </p>
          </div>

          <div style={{ padding: "1rem", background: "rgba(0,0,0,0.25)", borderRadius: "8px", border: "1px solid rgba(255,255,255,0.04)" }}>
            <h3 style={{ fontSize: "0.875rem", fontWeight: 700, color: "#86EFAC", marginBottom: "0.35rem" }}>
              Subsystem B: Qualitative Research Evidence Console (Intelligence)
            </h3>
            <p style={{ fontSize: "0.8125rem", color: "#94A3B8", lineHeight: 1.45 }}>
              Server-side RAG engine indexing 308 research cases (245 Play Store, 38 Reddit, 25 Interviews) with 3-gate verbatim quote verification. Implementation scheduled for Step 7.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
