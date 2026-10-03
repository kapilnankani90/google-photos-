"use client";

import { useState, useCallback } from "react";
import {
  Search,
  Sparkles,
  Layers,
  Database,
  AlertCircle,
  CheckCircle2,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  Tag,
  Clock,
  MapPin,
  Users,
  Compass,
  FileCode,
  ShieldAlert,
  Info,
} from "lucide-react";
import {
  DiscoveryResponse,
  CandidateResult,
  CanonicalCase,
} from "../types/discovery";

// Canonical 8 benchmark cases from part1_experimental_benchmark.json & Phase 3 suite
const CANONICAL_CASES: CanonicalCase[] = [
  {
    id: "case-1",
    title: "Case 1: Kinship & Cardinality",
    query: "5 sisters",
    category: "Kinship Gap",
    description: "Evaluates social role 'sister' with explicit group count 5.",
  },
  {
    id: "case-2",
    title: "Case 2: Multilingual Hinglish",
    query: "rohtang ki ice wali photo",
    category: "Hinglish Location",
    description: "Evaluates colloquial Hinglish 'ki ... wali' with spatial anchor 'rohtang' and prop 'ice'.",
  },
  {
    id: "case-3",
    title: "Case 3: Bound Attribute",
    query: "white bike",
    category: "Attribute Binding",
    description: "Tests compositional modifier 'white' bound specifically to 'bike' with +1.5 bonus.",
  },
  {
    id: "case-4",
    title: "Case 4: Cultural & Spatial Anchor",
    query: "diya at the gate",
    category: "Cultural Anchor",
    description: "Tests Diwali ritual anchor 'diya' bound to entrance boundary 'gate'.",
  },
  {
    id: "case-5",
    title: "Case 5: In-Image Alphanumeric Text",
    query: "Progressive",
    category: "OCR / Literal Text",
    description: "Tests literal alphanumeric brand/policy name printed on physical paperwork.",
  },
  {
    id: "case-6",
    title: "Case 6: Elapsed Temporal Anchor",
    query: "document around 4 years ago",
    category: "Relative Time",
    description: "Evaluates relative elapsed offset ('around 4 years ago') mapped to coarse era.",
  },
  {
    id: "case-7",
    title: "Case 7: Multi-Session Project Span",
    query: "yellow truck",
    category: "Temporal Cluster",
    description: "Tests controlled recovery broadening across a multi-day utility project span.",
  },
  {
    id: "case-8",
    title: "Case 8: Event Context Broad",
    query: "wedding",
    category: "Event Occasion",
    description: "Tests broad milestone occasion retrieval across diverse sub-events and albums.",
  },
];

export default function DiscoveryEngineConsole() {
  const [query, setQuery] = useState<string>("rohtang ki ice wali photo");
  const [topK, setTopK] = useState<number>(10);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<DiscoveryResponse | null>(null);
  const [showRawJson, setShowRawJson] = useState<boolean>(false);
  const [selectedCaseId, setSelectedCaseId] = useState<string>("case-2");

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

  const executeDiscovery = useCallback(async (searchQuery: string, kLimit: number) => {
    if (!searchQuery.trim()) {
      setError("Please enter a memory query or select a canonical benchmark case.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${apiBaseUrl}/api/v1/discover`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          raw_input: searchQuery.trim(),
          top_k: kLimit,
          enable_recovery: true,
        }),
      });

      if (!res.ok) {
        let errorDetail = `HTTP ${res.status}: ${res.statusText}`;
        try {
          const errData = await res.json();
          if (errData && errData.detail) {
            errorDetail = typeof errData.detail === "string" ? errData.detail : JSON.stringify(errData.detail);
          }
        } catch {
          // Fallback to status text
        }
        throw new Error(errorDetail);
      }

      const data: DiscoveryResponse = await res.json();
      setResponse(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to execute Discovery Engine retrieval.";
      setError(msg);
      setResponse(null);
    } finally {
      setLoading(false);
    }
  }, [apiBaseUrl]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    executeDiscovery(query, topK);
  };

  const handleSelectBenchmark = (c: CanonicalCase) => {
    setSelectedCaseId(c.id);
    setQuery(c.query);
    executeDiscovery(c.query, topK);
  };

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
            <h1 className="brand-title">Google Photos AI-Powered Discovery Engine</h1>
            <p className="brand-subtitle">Deliverable 1 — Evaluator &amp; Research Console (Stages 2–6 Retrieval)</p>
          </div>
        </div>

        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <span className="badge badge-connected">
            <span className="pulse-dot" />
            Engine Mode: Lexical FTS (Zero Embeddings)
          </span>
        </div>
      </header>

      {/* Deliverable 1 Product Boundary Callout */}
      <div className="boundary-banner">
        <Compass size={20} color="#60A5FA" style={{ flexShrink: 0, marginTop: "2px" }} />
        <div>
          <div className="boundary-banner-title">
            Deliverable 1 Architectural Scope Boundary
          </div>
          <div className="boundary-banner-text">
            This console is the <strong>Evaluator-Facing Discovery Engine</strong> demonstrating episodic memory interpretation (Stage 2), multi-signal derivation (Stage 3), PostgreSQL GIN tsvector retrieval &amp; controlled recovery (Stage 4), and compositional bound-attribute ranking (Stages 5–6).
            <span style={{ display: "block", marginTop: "0.25rem", color: "#93C5FD" }}>
              Note: This is <strong>NOT</strong> the separate consumer-facing AI-Native MVP (Deliverable 2).
            </span>
          </div>
        </div>
      </div>

      {/* Query Search Card */}
      <div className="search-box-wrapper">
        <form onSubmit={handleSearchSubmit}>
          <div className="search-input-row">
            <input
              type="text"
              className="search-input"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setSelectedCaseId("");
              }}
              placeholder="Enter episodic memory description (e.g., rohtang ki ice wali photo, 5 sisters...)"
              disabled={loading}
            />

            <div className="topk-select-wrapper">
              <span>Top K:</span>
              <select
                className="topk-select"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                disabled={loading}
              >
                <option value={3}>3</option>
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={20}>20</option>
              </select>
            </div>

            <button
              type="submit"
              className="btn-primary"
              disabled={loading || !query.trim()}
            >
              {loading ? (
                <>
                  <RefreshCw size={16} className="spin-animation" style={{ animation: "spin 1s linear infinite" }} />
                  <span>Discovering...</span>
                </>
              ) : (
                <>
                  <Search size={16} />
                  <span>Discover Evidence</span>
                </>
              )}
            </button>
          </div>
        </form>

        {/* 8 Canonical Benchmark Cases Selector */}
        <div className="benchmarks-section">
          <div className="benchmarks-title">
            <Sparkles size={14} color="#FBBC05" />
            <span>Canonical Benchmark Test Suite (Phase 3 Verified)</span>
          </div>
          <div className="benchmarks-grid">
            {CANONICAL_CASES.map((c) => (
              <button
                key={c.id}
                type="button"
                className={`benchmark-chip ${selectedCaseId === c.id ? "active" : ""}`}
                onClick={() => handleSelectBenchmark(c)}
                disabled={loading}
              >
                <span className="benchmark-chip-query">&ldquo;{c.query}&rdquo;</span>
                <span className="benchmark-chip-label">{c.title} • {c.category}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div
          style={{
            display: "flex",
            alignItems: "flex-start",
            gap: "0.75rem",
            padding: "1rem 1.25rem",
            background: "rgba(234, 67, 53, 0.12)",
            border: "1px solid rgba(234, 67, 53, 0.35)",
            borderRadius: "12px",
            marginBottom: "1.75rem",
            color: "#FCA5A5",
            fontSize: "0.875rem",
          }}
        >
          <ShieldAlert size={18} color="#EF4444" style={{ flexShrink: 0, marginTop: "2px" }} />
          <div>
            <strong>Retrieval Error:</strong> {error}
            <div style={{ marginTop: "0.25rem", fontSize: "0.75rem", color: "#F87171" }}>
              Verify the FastAPI backend is running locally at <code>{apiBaseUrl}</code> with <code>DATABASE_URL</code> configured.
            </div>
          </div>
        </div>
      )}

      {/* Pipeline Stage Trace (Stages 2, 3, 4) */}
      {response && (
        <div className="trace-grid-3col">
          {/* Stage 2: Memory Interpretation */}
          <div className="stage-card">
            <div className="stage-header">
              <span className="stage-title">Stage 2: Memory Interpretation</span>
              <span className="stage-number-badge">V2 Frame</span>
            </div>

            <div className="stage-body">
              {/* People */}
              <div className="concept-item">
                <span className="concept-label">
                  <Users size={12} style={{ display: "inline", marginRight: "4px" }} />
                  People / Kinship
                </span>
                <div className="concept-value">
                  {response.v2_frame.people && response.v2_frame.people.length > 0 ? (
                    response.v2_frame.people.map((p, idx) => (
                      <span key={idx} className="chip-tag chip-tag-blue">
                        {p.count ? `${p.count}× ` : ""}{p.role}
                        {p.attributes && p.attributes.length > 0 ? ` (${p.attributes.join(", ")})` : ""}
                      </span>
                    ))
                  ) : (
                    <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>None identified</span>
                  )}
                </div>
              </div>

              {/* Objects */}
              <div className="concept-item">
                <span className="concept-label">
                  <Tag size={12} style={{ display: "inline", marginRight: "4px" }} />
                  Salient Objects &amp; Modifiers
                </span>
                <div className="concept-value">
                  {response.v2_frame.objects && response.v2_frame.objects.length > 0 ? (
                    response.v2_frame.objects.map((o, idx) => (
                      <span key={idx} className="chip-tag chip-tag-yellow">
                        {o.name}
                        {o.attributes && o.attributes.length > 0 ? ` [${o.attributes.join(", ")}]` : ""}
                      </span>
                    ))
                  ) : (
                    <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>None identified</span>
                  )}
                </div>
              </div>

              {/* Spatial Setting */}
              <div className="concept-item">
                <span className="concept-label">
                  <MapPin size={12} style={{ display: "inline", marginRight: "4px" }} />
                  Spatial / Geographic Setting
                </span>
                <div className="concept-value">
                  {response.v2_frame.spatial_setting ? (
                    <span className="chip-tag chip-tag-green">{response.v2_frame.spatial_setting}</span>
                  ) : (
                    <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>None identified</span>
                  )}
                </div>
              </div>

              {/* Temporal */}
              <div className="concept-item">
                <span className="concept-label">
                  <Clock size={12} style={{ display: "inline", marginRight: "4px" }} />
                  Temporal Anchor
                </span>
                <div className="concept-value">
                  {response.v2_frame.temporal ? (
                    <span className="chip-tag chip-tag-purple">
                      {response.v2_frame.temporal.raw_time_expression}
                      {response.v2_frame.temporal.temporal_nature ? ` (${response.v2_frame.temporal.temporal_nature})` : ""}
                    </span>
                  ) : (
                    <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>None identified</span>
                  )}
                </div>
              </div>

              {/* Events & Literal Text */}
              {(response.v2_frame.events || (response.v2_frame.literal_text && response.v2_frame.literal_text.length > 0)) && (
                <div className="concept-item">
                  <span className="concept-label">Events &amp; Literal OCR Text</span>
                  <div className="concept-value">
                    {response.v2_frame.events && (
                      <span className="chip-tag chip-tag-blue">Event: {response.v2_frame.events.event_name}</span>
                    )}
                    {response.v2_frame.literal_text?.map((txt, idx) => (
                      <span key={idx} className="chip-tag">&ldquo;{txt}&rdquo;</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Stage 3: Retrieval Signal Generation */}
          <div className="stage-card">
            <div className="stage-header">
              <span className="stage-title">Stage 3: Retrieval Signals</span>
              <span className="stage-number-badge">Search Primitives</span>
            </div>

            <div className="stage-body">
              {/* Search Query Terms */}
              <div className="concept-item">
                <span className="concept-label">PostgreSQL FTS Query Terms</span>
                <div className="concept-value">
                  {response.retrieval_signals.search_query_terms && response.retrieval_signals.search_query_terms.length > 0 ? (
                    response.retrieval_signals.search_query_terms.map((term, idx) => (
                      <span key={idx} className="chip-tag chip-tag-blue" style={{ fontFamily: "var(--font-mono)" }}>
                        {term}
                      </span>
                    ))
                  ) : (
                    <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>Zero search terms</span>
                  )}
                </div>
              </div>

              {/* Bound Attributes */}
              <div className="concept-item">
                <span className="concept-label">Compositional Bound Attributes</span>
                <div className="concept-value">
                  {response.retrieval_signals.bound_attributes && response.retrieval_signals.bound_attributes.length > 0 ? (
                    response.retrieval_signals.bound_attributes.map((ba, idx) => {
                      const entity = String((ba as Record<string, unknown>).entity || "entity");
                      const attr = String((ba as Record<string, unknown>).attribute || "attribute");
                      return (
                        <span key={idx} className="chip-tag chip-tag-yellow">
                          {entity} ⇄ {attr}
                        </span>
                      );
                    })
                  ) : (
                    <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>No bound entity-attribute pairs</span>
                  )}
                </div>
              </div>

              {/* Visual Entities */}
              <div className="concept-item">
                <span className="concept-label">Visual Entities</span>
                <div className="concept-value">
                  {response.retrieval_signals.visual_entities && response.retrieval_signals.visual_entities.length > 0 ? (
                    response.retrieval_signals.visual_entities.map((ent, idx) => (
                      <span key={idx} className="chip-tag">
                        {ent}
                      </span>
                    ))
                  ) : (
                    <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>None</span>
                  )}
                </div>
              </div>

              {/* Spatial Cues */}
              <div className="concept-item">
                <span className="concept-label">Spatial &amp; Location Cues</span>
                <div className="concept-value">
                  {response.retrieval_signals.spatial_cues && response.retrieval_signals.spatial_cues.length > 0 ? (
                    response.retrieval_signals.spatial_cues.map((sc, idx) => (
                      <span key={idx} className="chip-tag chip-tag-green">
                        {sc}
                      </span>
                    ))
                  ) : (
                    <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>None</span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Stage 4: Coverage Checking & Recovery */}
          <div className="stage-card">
            <div className="stage-header">
              <span className="stage-title">Stage 4: Coverage &amp; Recovery</span>
              <span className="stage-number-badge">Candidate Discovery</span>
            </div>

            <div className="stage-body">
              {/* Coverage Status */}
              <div className="concept-item">
                <span className="concept-label">Candidate Coverage Outcome</span>
                <div className="concept-value">
                  <span className="chip-tag chip-tag-blue" style={{ fontWeight: 700 }}>
                    {response.coverage_status}
                  </span>
                </div>
              </div>

              {/* Controlled Recovery Callout */}
              {response.controlled_recovery_triggered ? (
                <div className="recovery-banner-active">
                  <AlertCircle size={16} />
                  <div>
                    Controlled Recovery Triggered
                    <div style={{ fontSize: "0.6875rem", fontWeight: 400, color: "#FEF08A" }}>
                      Initial candidate volume was insufficient. Automated broadening pass executed successfully.
                    </div>
                  </div>
                </div>
              ) : (
                <div className="recovery-banner-inactive">
                  <CheckCircle2 size={16} />
                  <div>
                    Initial Pass Sufficient
                    <div style={{ fontSize: "0.6875rem", fontWeight: 400, color: "#BBF7D0" }}>
                      Target coverage criteria met without requiring broadening recovery.
                    </div>
                  </div>
                </div>
              )}

              {/* Pool Size & Architecture */}
              <div className="concept-item">
                <span className="concept-label">Candidate Pool Volume</span>
                <div className="status-row" style={{ padding: "0.4rem 0.6rem" }}>
                  <span className="status-label">Total Recovered:</span>
                  <span className="status-val" style={{ color: "#4ADE80" }}>
                    {response.candidate_pool_size} candidate chunks
                  </span>
                </div>
                <div className="status-row" style={{ padding: "0.4rem 0.6rem" }}>
                  <span className="status-label">Ranked Top K:</span>
                  <span className="status-val">{response.results.length} returned</span>
                </div>
                <div className="status-row" style={{ padding: "0.4rem 0.6rem" }}>
                  <span className="status-label">Active Index:</span>
                  <span className="status-val" style={{ fontSize: "0.6875rem" }}>PostgreSQL GIN (idx_chunks_fts)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stage 5 & 6: Ranked Candidate Results */}
      {response && (
        <section className="results-section">
          <div className="results-header">
            <h2 className="results-title">
              <Layers size={20} color="#4285F4" />
              <span>Ranked Candidate Evidence Results</span>
            </h2>
            <span className="results-count-badge">
              Showing {response.results.length} of {response.candidate_pool_size} discovered
            </span>
          </div>

          {response.results.length === 0 ? (
            <div className="card" style={{ textAlign: "center", padding: "3rem 1.5rem" }}>
              <Info size={32} color="#94A3B8" style={{ margin: "0 auto 1rem auto" }} />
              <h3 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "0.5rem" }}>No Candidates Found</h3>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem", maxWidth: "500px", margin: "0 auto" }}>
                Zero candidate records matched the tsvector FTS query. Try broadening your memory description or select one of the 8 canonical benchmark queries above.
              </p>
            </div>
          ) : (
            response.results.map((cand: CandidateResult) => {
              const hasBoundBonus = cand.score_breakdown.bound_bonus > 0;
              const isRankOne = cand.rank === 1;

              return (
                <div key={cand.candidate_id} className="candidate-card">
                  <div className="candidate-card-header">
                    <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                      <span className={`rank-badge ${isRankOne ? "rank-badge-top" : ""}`}>
                        #{cand.rank}
                      </span>
                      <div>
                        <div style={{ fontSize: "0.875rem", fontWeight: 700, color: "var(--text-primary)" }}>
                          {cand.metadata.external_id || cand.candidate_id}
                          {cand.chunk_type && (
                            <span style={{ fontSize: "0.6875rem", color: "var(--text-muted)", marginLeft: "0.5rem" }}>
                              [{cand.chunk_type}]
                            </span>
                          )}
                        </div>
                        <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                          Methodology: {cand.metadata.methodology || "UNSOLICITED_PUBLIC"}
                          {cand.metadata.failure_mode ? ` • ${cand.metadata.failure_mode}` : ""}
                        </div>
                      </div>
                    </div>

                    <div className="score-cluster">
                      {hasBoundBonus && (
                        <span className="bound-bonus-badge">
                          +1.5 Bound Bonus
                        </span>
                      )}
                      <span className="total-score-pill">
                        Score: {cand.score.toFixed(4)}
                      </span>
                    </div>
                  </div>

                  {/* Verbatim Content */}
                  <div className="evidence-content">
                    {cand.content}
                  </div>

                  {/* Card Footer: Score breakdown and metadata tags */}
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
                    <div className="score-breakdown-details">
                      <span>RRF Base: {cand.score_breakdown.base_rrf.toFixed(4)}</span>
                      <span>Bound Bonus: {cand.score_breakdown.bound_bonus.toFixed(2)}</span>
                      <span>Penalty: {cand.score_breakdown.distractor_penalty.toFixed(2)}</span>
                    </div>

                    <div className="candidate-metadata-row">
                      {cand.metadata.evidence_type && (
                        <span className="metadata-pill" style={{ color: cand.metadata.evidence_type === "FAILURE" ? "#FCA5A5" : "#86EFAC" }}>
                          Type: {cand.metadata.evidence_type}
                        </span>
                      )}
                      {cand.metadata.category_tags && Array.isArray(cand.metadata.category_tags) && (
                        cand.metadata.category_tags.slice(0, 3).map((tag, tIdx) => (
                          <span key={tIdx} className="metadata-pill">
                            {tag}
                          </span>
                        ))
                      )}
                      <span className="metadata-pill" style={{ fontFamily: "var(--font-mono)" }}>
                        Path: {cand.retrieval_paths.join(", ")}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </section>
      )}

      {/* Expandable Raw Debug Drawer */}
      {response && (
        <div>
          <button
            type="button"
            className="raw-debug-toggle"
            onClick={() => setShowRawJson(!showRawJson)}
          >
            <FileCode size={14} />
            <span>{showRawJson ? "Hide" : "Inspect"} Section 18.2 Raw DiscoveryResponse JSON</span>
            {showRawJson ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>

          {showRawJson && (
            <pre className="raw-debug-box">
              {JSON.stringify(response, null, 2)}
            </pre>
          )}
        </div>
      )}

      {/* Initial Empty State before search */}
      {!response && !loading && !error && (
        <div className="card" style={{ textAlign: "center", padding: "3rem 1.5rem" }}>
          <Database size={40} color="#4285F4" style={{ margin: "0 auto 1.25rem auto" }} />
          <h2 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: "0.5rem" }}>
            Ready to Evaluate Algorithmic Retrieval
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem", maxWidth: "600px", margin: "0 auto 1.5rem auto", lineHeight: 1.5 }}>
            Type an arbitrary episodic memory query or select one of the 8 canonical benchmark cases above to execute the live multi-path discovery pipeline against Supabase PostgreSQL.
          </p>
          <div style={{ display: "inline-flex", gap: "0.75rem", flexWrap: "wrap", justifyContent: "center" }}>
            <span className="badge">Stage 2: Memory Interpretation</span>
            <span className="badge">Stage 3: Signal Derivation</span>
            <span className="badge">Stage 4: PostgreSQL GIN FTS</span>
            <span className="badge">Stage 5: Bound Attribute Bonus</span>
            <span className="badge">Stage 6: RRF Composite Ranking</span>
          </div>
        </div>
      )}
    </main>
  );
}
