"use client";

import { useState, useCallback } from "react";
import {
  Search,
  Sparkles,
  Layers,
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
    title: "5 sisters",
    query: "5 sisters",
    category: "Kinship",
    description: "Evaluates social role 'sister' with explicit group count 5.",
  },
  {
    id: "case-2",
    title: "rohtang ki ice wali photo",
    query: "rohtang ki ice wali photo",
    category: "Multilingual / Place",
    description: "Colloquial Hinglish memory with place 'rohtang' and prop 'ice'.",
  },
  {
    id: "case-3",
    title: "white bike",
    query: "white bike",
    category: "Bound Attribute",
    description: "Tests modifier 'white' bound specifically to 'bike'.",
  },
  {
    id: "case-4",
    title: "diya at the gate",
    query: "diya at the gate",
    category: "Cultural / Spatial",
    description: "Diwali ritual anchor 'diya' bound to entrance 'gate'.",
  },
  {
    id: "case-5",
    title: "Progressive",
    query: "Progressive",
    category: "In-Image Text",
    description: "Literal alphanumeric text printed on paperwork.",
  },
  {
    id: "case-6",
    title: "document around 4 years ago",
    query: "document around 4 years ago",
    category: "Relative Time",
    description: "Relative elapsed offset mapped to coarse era.",
  },
  {
    id: "case-7",
    title: "yellow truck",
    query: "yellow truck",
    category: "Expanded Search",
    description: "Tests search broadening across an episodic project span.",
  },
  {
    id: "case-8",
    title: "wedding",
    query: "wedding",
    category: "Occasion",
    description: "Broad milestone occasion retrieval across albums.",
  },
];

function getFriendlyEvidenceType(cand: CandidateResult): string {
  const chunkType = cand.chunk_type?.toUpperCase() || "";
  const evType = (cand.metadata?.evidence_type as string)?.toUpperCase() || "";

  if (chunkType === "RAW_QUOTE") return "User Evidence";
  if (chunkType === "SITUATION_SUMMARY") return "Case Summary";
  if (chunkType === "JTBD") return "User Goal";
  if (chunkType === "SOLUTION_FAILURE") return "Failure Case";

  if (evType === "RAW_QUOTE" || evType === "USER_EVIDENCE") return "User Evidence";
  if (evType === "FAILURE") return "Failure Case";
  if (evType === "NEUTRAL") return "User Case";
  if (evType === "SUCCESS") return "Success Case";

  if (chunkType) {
    return chunkType.replace(/_/g, " ").toLowerCase().replace(/\b\w/g, (l) => l.toUpperCase());
  }
  return "Evidence Record";
}

function getFriendlyCoverageStatus(status: string): string {
  if (status === "INSUFFICIENT_VOLUME") return "Not enough evidence found initially";
  if (status === "COVERAGE_SUFFICIENT" || status === "SUFFICIENT") return "Sufficient evidence found";
  return status.replace(/_/g, " ").toLowerCase().replace(/\b\w/g, (l) => l.toUpperCase());
}

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
      setError("Please enter a memory description or select an example memory.");
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
            <p className="brand-subtitle">Deliverable 1 — Evaluator Console</p>
          </div>
        </div>

        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <span className="badge badge-connected">
            <span className="pulse-dot" />
            Engine Mode: Lexical FTS (Zero Embeddings)
          </span>
        </div>
      </header>

      {/* Deliverable 1 Plain-English Scope Callout */}
      <div className="boundary-banner">
        <Compass size={20} color="#60A5FA" style={{ flexShrink: 0, marginTop: "2px" }} />
        <div>
          <div className="boundary-banner-title">
            Deliverable 1 — AI-Powered Discovery Engine
          </div>
          <div className="boundary-banner-text">
            This evaluator console shows how a vague memory is converted into search clues and used to retrieve relevant evidence.
            <span style={{ display: "block", marginTop: "0.25rem", color: "#93C5FD" }}>
              This is the Discovery Engine, not the separate consumer-facing Memory Search MVP.
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
              placeholder="Enter a memory description (e.g., rohtang ki ice wali photo, yellow kurta, 5 sisters...)"
              disabled={loading}
            />

            <div className="topk-select-wrapper" title="Choose how many evidence results to display.">
              <span>Results to show:</span>
              <select
                className="topk-select"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                disabled={loading}
                aria-label="Choose how many evidence results to display"
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

        {/* Example Memories */}
        <div className="benchmarks-section">
          <div className="benchmarks-title">
            <Sparkles size={14} color="#FBBC05" />
            <span>Try an example memory</span>
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
                <span className="benchmark-chip-label">{c.category}</span>
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

      {/* Three Main Stages: Understand Memory, Extract Clues, Find Evidence */}
      {response && (
        <div className="trace-grid-3col">
          {/* Card 1: Understand the Memory */}
          <div className="stage-card">
            <div className="stage-header">
              <span className="stage-title">1. Understand the Memory</span>
            </div>

            <div className="stage-body">
              {/* People */}
              <div className="concept-item">
                <span className="concept-label">
                  <Users size={12} style={{ display: "inline", marginRight: "4px" }} />
                  People
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

              {/* Objects & details */}
              <div className="concept-item">
                <span className="concept-label">
                  <Tag size={12} style={{ display: "inline", marginRight: "4px" }} />
                  Objects &amp; details
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

              {/* Place */}
              <div className="concept-item">
                <span className="concept-label">
                  <MapPin size={12} style={{ display: "inline", marginRight: "4px" }} />
                  Place
                </span>
                <div className="concept-value">
                  {response.v2_frame.spatial_setting ? (
                    <span className="chip-tag chip-tag-green">{response.v2_frame.spatial_setting}</span>
                  ) : (
                    <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>None identified</span>
                  )}
                </div>
              </div>

              {/* Time */}
              <div className="concept-item">
                <span className="concept-label">
                  <Clock size={12} style={{ display: "inline", marginRight: "4px" }} />
                  Time
                </span>
                <div className="concept-value">
                  {response.v2_frame.temporal ? (
                    <span className="chip-tag chip-tag-purple">
                      {response.v2_frame.temporal.raw_time_expression}
                    </span>
                  ) : (
                    <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>None identified</span>
                  )}
                </div>
              </div>

              {/* Events & Literal Text */}
              {(response.v2_frame.events || (response.v2_frame.literal_text && response.v2_frame.literal_text.length > 0)) && (
                <div className="concept-item">
                  <span className="concept-label">Events &amp; in-image text</span>
                  <div className="concept-value">
                    {response.v2_frame.events && (
                      <span className="chip-tag chip-tag-blue">{response.v2_frame.events.event_name}</span>
                    )}
                    {response.v2_frame.literal_text?.map((txt, idx) => (
                      <span key={idx} className="chip-tag">&ldquo;{txt}&rdquo;</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Card 2: Extract Search Clues */}
          <div className="stage-card">
            <div className="stage-header">
              <span className="stage-title">2. Extract Search Clues</span>
            </div>

            <div className="stage-body">
              {/* Search terms */}
              <div className="concept-item">
                <span className="concept-label">Search terms</span>
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

              {/* Objects detected */}
              <div className="concept-item">
                <span className="concept-label">Objects detected</span>
                <div className="concept-value">
                  {response.retrieval_signals.visual_entities && response.retrieval_signals.visual_entities.length > 0 ? (
                    response.retrieval_signals.visual_entities.map((ent, idx) => (
                      <span key={idx} className="chip-tag">
                        {ent}
                      </span>
                    ))
                  ) : (
                    <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>None identified</span>
                  )}
                </div>
              </div>

              {/* Place / location */}
              <div className="concept-item">
                <span className="concept-label">Place / location</span>
                <div className="concept-value">
                  {response.retrieval_signals.spatial_cues && response.retrieval_signals.spatial_cues.length > 0 ? (
                    response.retrieval_signals.spatial_cues.map((sc, idx) => (
                      <span key={idx} className="chip-tag chip-tag-green">
                        {sc}
                      </span>
                    ))
                  ) : (
                    <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>None identified</span>
                  )}
                </div>
              </div>

              {/* Other clues */}
              <div className="concept-item">
                <span className="concept-label">Other clues</span>
                <div className="concept-value">
                  {response.retrieval_signals.bound_attributes && response.retrieval_signals.bound_attributes.length > 0 ? (
                    response.retrieval_signals.bound_attributes.map((ba, idx) => {
                      const entity = String((ba as Record<string, unknown>).entity || "entity");
                      const attr = String((ba as Record<string, unknown>).attribute || "attribute");
                      return (
                        <span key={idx} className="chip-tag chip-tag-yellow">
                          {attr} {entity}
                        </span>
                      );
                    })
                  ) : response.retrieval_signals.action_signals && response.retrieval_signals.action_signals.length > 0 ? (
                    response.retrieval_signals.action_signals.map((act, idx) => (
                      <span key={idx} className="chip-tag chip-tag-purple">
                        {act}
                      </span>
                    ))
                  ) : (
                    <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>None identified</span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Card 3: Find Relevant Evidence */}
          <div className="stage-card">
            <div className="stage-header">
              <span className="stage-title">3. Find Relevant Evidence</span>
            </div>

            <div className="stage-body">
              {/* Did we find enough evidence? */}
              <div className="concept-item">
                <span className="concept-label">Did we find enough evidence?</span>
                <div className="concept-value">
                  <span className="chip-tag chip-tag-blue" style={{ fontWeight: 600 }}>
                    {getFriendlyCoverageStatus(response.coverage_status)}
                  </span>
                </div>
              </div>

              {/* Expanded search used / Initial search sufficient */}
              {response.controlled_recovery_triggered ? (
                <div className="recovery-banner-active">
                  <AlertCircle size={16} style={{ flexShrink: 0 }} />
                  <div>
                    Expanded search used
                    <div style={{ fontSize: "0.6875rem", fontWeight: 400, color: "#FEF08A" }}>
                      Initial search found limited matches, so an expanded search was run automatically.
                    </div>
                  </div>
                </div>
              ) : (
                <div className="recovery-banner-inactive">
                  <CheckCircle2 size={16} style={{ flexShrink: 0 }} />
                  <div>
                    Initial search sufficient
                    <div style={{ fontSize: "0.6875rem", fontWeight: 400, color: "#BBF7D0" }}>
                      Found enough matching evidence without needing an expanded search.
                    </div>
                  </div>
                </div>
              )}

              {/* Evidence stats */}
              <div className="concept-item">
                <div className="status-row" style={{ padding: "0.4rem 0.6rem" }}>
                  <span className="status-label">Evidence found:</span>
                  <span className="status-val" style={{ color: "#4ADE80" }}>
                    {response.candidate_pool_size} items
                  </span>
                </div>
                <div className="status-row" style={{ padding: "0.4rem 0.6rem" }}>
                  <span className="status-label">Results shown:</span>
                  <span className="status-val">{response.results.length} results</span>
                </div>
                <div className="status-row" style={{ padding: "0.4rem 0.6rem" }}>
                  <span className="status-label">Recovery used:</span>
                  <span className="status-val">{response.controlled_recovery_triggered ? "Yes (expanded search)" : "No"}</span>
                </div>
              </div>

              {/* Collapsed Technical details */}
              <details className="tech-details-dropdown">
                <summary className="tech-details-summary">Technical details</summary>
                <div className="tech-details-content">
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.3rem", fontSize: "0.75rem" }}>
                    <div><span className="tech-label">Coverage Status:</span> <span className="tech-val">{response.coverage_status}</span></div>
                    <div><span className="tech-label">Active Index:</span> <span className="tech-val">PostgreSQL GIN (idx_chunks_fts)</span></div>
                    <div><span className="tech-label">Candidate Pool Size:</span> <span className="tech-val">{response.candidate_pool_size}</span></div>
                  </div>
                </div>
              </details>
            </div>
          </div>
        </div>
      )}

      {/* Retrieved Evidence */}
      {response && (
        <section className="results-section">
          {/* Query context banner to make query-dependent results crystal clear */}
          <div className="results-context-banner">
            <div className="results-context-query">
              Evidence retrieved for: <strong>&ldquo;{response.raw_input || query}&rdquo;</strong>
            </div>
            <div className="results-context-hint">
              The results below are based on the memory entered above.
            </div>
          </div>

          <div className="results-header">
            <div>
              <h2 className="results-title">
                <Layers size={20} color="#4285F4" />
                <span>Retrieved Evidence</span>
              </h2>
              <p className="results-subtitle">
                These are the evidence records the engine found for the user&apos;s memory.
              </p>
            </div>
            <span className="results-count-badge">
              Showing {response.results.length} of {response.candidate_pool_size} found
            </span>
          </div>

          {response.results.length === 0 ? (
            <div className="card" style={{ textAlign: "center", padding: "3rem 1.5rem" }}>
              <Info size={32} color="#94A3B8" style={{ margin: "0 auto 1rem auto" }} />
              <h3 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "0.5rem" }}>No Evidence Found</h3>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem", maxWidth: "500px", margin: "0 auto" }}>
                Zero evidence records matched this description. Try entering a different memory or select one of the example memories above.
              </p>
            </div>
          ) : (
            response.results.map((cand: CandidateResult) => {
              const friendlyType = getFriendlyEvidenceType(cand);

              return (
                <div key={cand.candidate_id} className="candidate-card">
                  <div className="candidate-card-header">
                    <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                      <span className="rank-badge">
                        #{cand.rank}
                      </span>
                      <div>
                        <div style={{ fontSize: "0.9375rem", fontWeight: 700, color: "var(--text-primary)" }}>
                          Result {cand.rank}
                          <span className="chip-tag chip-tag-blue" style={{ marginLeft: "0.5rem", fontSize: "0.75rem", fontWeight: 600 }}>
                            {friendlyType}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Verbatim Content */}
                  <div className="evidence-content">
                    {cand.content}
                  </div>

                  {/* Card Footer: Metadata tags & Collapsible Technical Details */}
                  <div className="candidate-card-footer">
                    {cand.metadata.category_tags && Array.isArray(cand.metadata.category_tags) && cand.metadata.category_tags.length > 0 && (
                      <div className="candidate-metadata-row">
                        {cand.metadata.category_tags.slice(0, 3).map((tag, tIdx) => (
                          <span key={tIdx} className="metadata-pill">
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}

                    <details className="tech-details-dropdown">
                      <summary className="tech-details-summary">
                        Technical details
                      </summary>
                      <div className="tech-details-content">
                        <div className="tech-details-grid">
                          <div>
                            <span className="tech-label">Internal Ranking Score:</span>{" "}
                            <span className="tech-val">{cand.score.toFixed(4)}</span>
                          </div>
                          <div>
                            <span className="tech-label">RRF Base:</span>{" "}
                            <span className="tech-val">{cand.score_breakdown.base_rrf.toFixed(4)}</span>
                          </div>
                          <div>
                            <span className="tech-label">Bound Bonus:</span>{" "}
                            <span className="tech-val">{cand.score_breakdown.bound_bonus.toFixed(2)}</span>
                          </div>
                          <div>
                            <span className="tech-label">Penalty:</span>{" "}
                            <span className="tech-val">{cand.score_breakdown.distractor_penalty.toFixed(2)}</span>
                          </div>
                          <div>
                            <span className="tech-label">Retrieval Path:</span>{" "}
                            <span className="tech-val">{cand.retrieval_paths.join(", ") || "fts"}</span>
                          </div>
                          {cand.metadata.external_id && (
                            <div>
                              <span className="tech-label">External ID:</span>{" "}
                              <span className="tech-val">{String(cand.metadata.external_id)}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </details>
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
            <span>{showRawJson ? "Hide" : "Inspect"} Raw Response (JSON)</span>
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
          <Search size={40} color="#4285F4" style={{ margin: "0 auto 1.25rem auto" }} />
          <h2 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: "0.5rem" }}>
            Ready to Discover Evidence
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem", maxWidth: "560px", margin: "0 auto 1.5rem auto", lineHeight: 1.5 }}>
            Type a memory description above or select one of the example memories to see how the system understands the memory, extracts clues, and retrieves relevant evidence.
          </p>
          <div style={{ display: "inline-flex", gap: "0.75rem", flexWrap: "wrap", justifyContent: "center" }}>
            <span className="badge">1. Understand Memory</span>
            <span className="badge">2. Extract Search Clues</span>
            <span className="badge">3. Find Evidence</span>
          </div>
        </div>
      )}
    </main>
  );
}
