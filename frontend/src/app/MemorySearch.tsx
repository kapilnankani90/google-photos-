"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import {
  Search,
  Sparkles,
  Mic,
  MicOff,
  RotateCcw,
  CheckCircle2,
  BookmarkCheck,
  MapPin,
  Users,
  Tag,
  Clock,
  Calendar,
  ArrowRight,
  AlertCircle,
  Heart,
  Compass,
} from "lucide-react";
import { DiscoveryResponse, CandidateResult, MemorySearchResponse } from "../types/discovery";

interface CuratedMemory {
  id: string;
  category: "Place / Context" | "People / Count" | "Object / Modifier" | "Time-Relative" | "Occasion / Anchor";
  icon: string;
  label: string;
  memoryText: string;
  hint: string;
}

const CURATED_MEMORIES: CuratedMemory[] = [
  {
    id: "mem-fuzzy-sea",
    category: "Place / Context",
    icon: "🌅",
    label: "Sunset near sea in Goa",
    memoryText: "I'm looking for that photo from a trip where I was standing near the sea at sunset, maybe around Goa, and I think my friends were with me.",
    hint: "Conversational fuzzy memory demonstrating Groq NLU dimension extraction & ambiguity clarification",
  },
  {
    id: "mem-place",
    category: "Place / Context",
    icon: "🏔️",
    label: "Trip in the snow",
    memoryText: "A cold trip with ice and snow in Rohtang",
    hint: "Contextual memory with location and weather features",
  },
  {
    id: "mem-people",
    category: "People / Count",
    icon: "👥",
    label: "5 sisters together",
    memoryText: "A photo with my 5 sisters together",
    hint: "Social kinship memory with exact count",
  },
  {
    id: "mem-object",
    category: "Object / Modifier",
    icon: "🚲",
    label: "White bicycle",
    memoryText: "A picture with that white bike",
    hint: "Salient physical prop with bound color modifier",
  },
  {
    id: "mem-time",
    category: "Time-Relative",
    icon: "⏳",
    label: "Document 4 years ago",
    memoryText: "A document from around 4 years ago",
    hint: "Temporal anchor expressed as elapsed relative offset",
  },
  {
    id: "mem-spatial",
    category: "Occasion / Anchor",
    icon: "🪔",
    label: "Diya by the gate",
    memoryText: "Diya lit at the entrance gate",
    hint: "Cultural occasion detail tied to architectural anchor",
  },
  {
    id: "mem-occasion",
    category: "Occasion / Anchor",
    icon: "🎊",
    label: "Wedding celebration",
    memoryText: "A family wedding celebration",
    hint: "Broad milestone event across personal albums",
  },
];

const REFINEMENT_PROMPTS = [
  { label: "+ Add people", text: " with my family and friends" },
  { label: "+ Add place", text: " somewhere outdoors in the mountains" },
  { label: "+ Add colors", text: " wearing bright yellow clothes" },
  { label: "+ Add approximate time", text: " from around 2 or 3 years ago" },
  { label: "+ Add season", text: " during winter trip" },
];

export type VoiceStatus = "idle" | "listening" | "transcribing" | "unsupported" | "error";

export interface VoiceNotice {
  text: string;
  level: "info" | "listening" | "transcribing" | "success" | "error";
}

export default function MemorySearch() {
  const [memoryInput, setMemoryInput] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<MemorySearchResponse | DiscoveryResponse | null>(null);
  const [clarificationInput, setClarificationInput] = useState<string>("" );
  const [recognizedIds, setRecognizedIds] = useState<Set<string>>(new Set());

  // MediaRecorder audio capture state
  const [voiceStatus, setVoiceStatus] = useState<VoiceStatus>("idle");
  const [voiceNotice, setVoiceNotice] = useState<VoiceNotice | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const mediaStreamRef = useRef<MediaStream | null>(null);

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

  // Check MediaRecorder capability on client mount
  useEffect(() => {
    if (typeof window !== "undefined") {
      if (!navigator?.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
        setVoiceStatus("unsupported");
      }
    }
  }, []);

  const executeMemorySearch = useCallback(
    async (queryText: string) => {
      const cleanText = queryText.trim();
      if (!cleanText) return;

      setLoading(true);
      setError(null);

      try {
        let res = await fetch(`${apiBaseUrl}/api/v1/memory/search`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            raw_input: cleanText,
            top_k: 8,
            enable_recovery: true,
          }),
        });

        // Graceful fallback to legacy /discover if /memory/search is not available
        if (res.status === 404) {
          res = await fetch(`${apiBaseUrl}/api/v1/discover`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              raw_input: cleanText,
              top_k: 8,
              enable_recovery: true,
            }),
          });
        }

        if (!res.ok) {
          let errorDetail = `Service error (${res.status})`;
          try {
            const errData = await res.json();
            if (errData?.detail) {
              errorDetail = typeof errData.detail === "string" ? errData.detail : JSON.stringify(errData.detail);
            }
          } catch {
            // Keep status string
          }
          throw new Error(errorDetail);
        }

        const data = await res.json();
        setResponse(data);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Unable to retrieve memories right now.";
        setError(msg);
      } finally {
        setLoading(false);
      }
    },
    [apiBaseUrl]
  );

  const handleClarificationSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!clarificationInput.trim() || loading) return;
    const refined = `${memoryInput.trim()}, ${clarificationInput.trim()}`;
    setMemoryInput(refined);
    setClarificationInput("");
    executeMemorySearch(refined);
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (loading || voiceStatus === "transcribing" || voiceStatus === "listening") {
      return;
    }
    executeMemorySearch(memoryInput);
  };

  const handleSelectCurated = (m: CuratedMemory) => {
    setMemoryInput(m.memoryText);
    executeMemorySearch(m.memoryText);
  };

  const toggleRecognized = (candidateId: string) => {
    setRecognizedIds((prev) => {
      const next = new Set(prev);
      if (next.has(candidateId)) {
        next.delete(candidateId);
      } else {
        next.add(candidateId);
      }
      return next;
    });
  };

  const applyRefinement = (addition: string) => {
    const updated = `${memoryInput.trim()}${addition}`;
    setMemoryInput(updated);
    executeMemorySearch(updated);
  };

  const handleVoiceToggle = async () => {
    if (typeof window === "undefined") return;

    if (voiceStatus === "unsupported") {
      setVoiceNotice({
        text: "Audio recording is not supported in this browser. You can type your memory instead.",
        level: "info",
      });
      return;
    }

    // Ignore toggle requests while transcribing
    if (voiceStatus === "transcribing") {
      return;
    }

    // If currently listening, stop recording -> onstop sends audio to backend
    if (voiceStatus === "listening") {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
        try {
          mediaRecorderRef.current.stop();
        } catch {
          // recorder might have already stopped
        }
      }
      return;
    }

    // Start a new recording session
    try {
      if (!navigator?.mediaDevices?.getUserMedia) {
        setVoiceStatus("unsupported");
        setVoiceNotice({
          text: "Audio recording is not supported in this browser. You can type your memory instead.",
          level: "info",
        });
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      // Select supported audio MIME type
      let chosenMime = "audio/webm";
      if (typeof MediaRecorder.isTypeSupported === "function") {
        if (MediaRecorder.isTypeSupported("audio/webm;codecs=opus")) {
          chosenMime = "audio/webm;codecs=opus";
        } else if (MediaRecorder.isTypeSupported("audio/webm")) {
          chosenMime = "audio/webm";
        } else if (MediaRecorder.isTypeSupported("audio/mp4")) {
          chosenMime = "audio/mp4";
        } else if (MediaRecorder.isTypeSupported("audio/ogg")) {
          chosenMime = "audio/ogg";
        }
      }

      const recorder = new MediaRecorder(stream, chosenMime ? { mimeType: chosenMime } : undefined);
      mediaRecorderRef.current = recorder;
      audioChunksRef.current = [];

      recorder.ondataavailable = (event: BlobEvent) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        // Free microphone tracks immediately
        if (mediaStreamRef.current) {
          mediaStreamRef.current.getTracks().forEach((track) => track.stop());
          mediaStreamRef.current = null;
        }

        const chunks = audioChunksRef.current;
        if (!chunks || chunks.length === 0) {
          setVoiceStatus("error");
          setVoiceNotice({
            text: "No audio was captured. Please click the microphone to try again.",
            level: "error",
          });
          return;
        }

        const mime = recorder.mimeType || chosenMime || "audio/webm";
        const audioBlob = new Blob(chunks, { type: mime });

        // Transition immediately to transcribing
        setVoiceStatus("transcribing");
        setVoiceNotice({
          text: "Transcribing your memory with Gemini...",
          level: "transcribing",
        });

        try {
          const formData = new FormData();
          formData.append("audio", audioBlob, "recording.webm");
          formData.append("mime_type", mime);

          const res = await fetch(`${apiBaseUrl}/api/v1/transcribe`, {
            method: "POST",
            body: formData,
          });

          if (!res.ok) {
            let errorDetail = `Transcription service error (${res.status})`;
            try {
              const errData = await res.json();
              if (errData?.detail) {
                errorDetail = typeof errData.detail === "string" ? errData.detail : JSON.stringify(errData.detail);
              }
            } catch {}
            throw new Error(errorDetail);
          }

          const data = await res.json();
          const text = (data.transcript || "").trim();

          if (!text) {
            setVoiceStatus("error");
            setVoiceNotice({
              text: "No speech recognized. Please speak your memory clearly and try again.",
              level: "error",
            });
            return;
          }

          // Populate the same memory input
          setMemoryInput(text);

          // State lifecycle: never stuck in 'finishing' or 'transcribing'
          setVoiceStatus("idle");
          setVoiceNotice({
            text: "Memory transcribed! Review or edit the text above, then click Find Memory.",
            level: "success",
          });
        } catch (err: unknown) {
          setVoiceStatus("error");
          const msg = err instanceof Error ? err.message : "Failed to transcribe audio.";
          setVoiceNotice({
            text: msg,
            level: "error",
          });
        }
      };

      recorder.start();
      setVoiceStatus("listening");
      setVoiceNotice({
        text: "Listening... speak your complete memory naturally (English or Hinglish)",
        level: "listening",
      });
    } catch (err: unknown) {
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((track) => track.stop());
        mediaStreamRef.current = null;
      }
      setVoiceStatus("error");
      if (err && typeof err === "object" && "name" in err) {
        const errorName = (err as { name: string }).name;
        if (errorName === "NotAllowedError" || errorName === "PermissionDeniedError") {
          setVoiceNotice({
            text: "Microphone permission denied. Please allow microphone access or type your memory.",
            level: "error",
          });
          return;
        }
      }
      setVoiceNotice({
        text: "Could not access microphone. You can type your memory above.",
        level: "error",
      });
    }
  };

  const clearSearch = () => {
    setMemoryInput("");
    setResponse(null);
    setError(null);
    setVoiceNotice(null);
  };

  // Helper to extract clean human-friendly clues from v2 frame or Groq structured clues
  const memorySearchResp = response && "structured_clues" in response ? (response as MemorySearchResponse) : null;
  const structuredClues = memorySearchResp?.structured_clues;
  const frame = response?.v2_frame;
  const hasClues =
    Boolean(structuredClues) ||
    Boolean(
      frame &&
      ((frame.people && frame.people.length > 0) ||
        frame.spatial_setting ||
        (frame.objects && frame.objects.length > 0) ||
        frame.temporal ||
        frame.events ||
        (frame.literal_text && frame.literal_text.length > 0))
    );

  return (
    <div className="ms-container">
      {/* Hero Presentation */}
      <section className="ms-hero">
        <div className="ms-hero-pill">
          <Sparkles size={14} color="#FBBC05" />
          <span>AI-Native Prototype · The Representation Gap Solution</span>
        </div>
        <h1 className="ms-hero-title">
          Search your photos <span className="ms-hero-gradient">the way you remember them</span>
        </h1>
        <p className="ms-hero-subtitle">
          You don&apos;t remember photos as database keywords. Describe the feeling, who was there, a salient object, or where you were, and the AI will interpret your memory to find the moment.
        </p>
      </section>

      {/* Primary Conversational Search Box */}
      <div className="ms-search-card">
        <form onSubmit={handleSearchSubmit} className="ms-search-form">
          <div className="ms-input-box">
            <div className="ms-input-icon">
              <Search size={22} color="var(--accent-blue)" />
            </div>

            <input
              type="text"
              className="ms-input-field"
              value={memoryInput}
              onChange={(e) => setMemoryInput(e.target.value)}
              placeholder={
                voiceStatus === "listening"
                  ? "Listening... speak your complete memory naturally..."
                  : voiceStatus === "transcribing"
                  ? "Transcribing your memory with Gemini..."
                  : "e.g. I remember a cold trip in the snow with my friends, or that picture with the white bike..."
              }
              disabled={loading || voiceStatus === "transcribing"}
            />

            {/* Clear Button */}
            {memoryInput && !loading && (
              <button
                type="button"
                onClick={clearSearch}
                className="ms-icon-btn ms-clear-btn"
                title="Clear memory"
                aria-label="Clear memory text"
              >
                ✕
              </button>
            )}

            {/* Voice Input Button */}
            <button
              type="button"
              onClick={handleVoiceToggle}
              disabled={voiceStatus === "transcribing"}
              className={`ms-icon-btn ms-mic-btn ms-mic-status-${voiceStatus} ${
                voiceStatus === "listening" ? "ms-mic-listening" : ""
              }`}
              title={
                voiceStatus === "unsupported"
                  ? "Audio recording isn't supported in this browser. You can type your memory instead."
                  : voiceStatus === "listening"
                  ? "Listening... Click to stop and transcribe"
                  : voiceStatus === "transcribing"
                  ? "Transcribing audio..."
                  : "Click to speak your memory (supports English, Hindi & Hinglish)"
              }
              aria-label={
                voiceStatus === "listening"
                  ? "Stop voice recording"
                  : "Start voice recording"
              }
            >
              {voiceStatus === "listening" ? (
                <MicOff size={20} color="#EA4335" />
              ) : voiceStatus === "transcribing" ? (
                <RotateCcw size={18} className="ms-spin" color="var(--accent-blue)" />
              ) : (
                <Mic
                  size={20}
                  color={voiceStatus === "unsupported" ? "var(--text-muted)" : "var(--text-secondary)"}
                />
              )}
            </button>

            {/* Primary Action Button */}
            <button
              type="submit"
              className="ms-submit-btn"
              disabled={loading || voiceStatus === "transcribing" || !memoryInput.trim()}
            >
              {loading ? (
                <>
                  <RotateCcw size={16} className="ms-spin" />
                  <span>Interpreting...</span>
                </>
              ) : (
                <>
                  <Sparkles size={16} />
                  <span>Find Memory</span>
                </>
              )}
            </button>
          </div>
        </form>

        {/* Voice Feedback / Notification Banner */}
        {voiceNotice && (
          <div className={`ms-voice-feedback ms-voice-feedback-${voiceNotice.level}`}>
            {voiceStatus === "listening" && <span className="ms-pulse-dot" />}
            {voiceStatus === "transcribing" && <RotateCcw size={14} className="ms-spin" />}
            <span className="ms-voice-feedback-text">{voiceNotice.text}</span>
            {voiceStatus === "listening" && (
              <button
                type="button"
                onClick={handleVoiceToggle}
                className="ms-voice-stop-chip"
                title="Finish speaking and transcribe"
              >
                Stop Speaking ■
              </button>
            )}
            {voiceStatus !== "listening" && voiceStatus !== "transcribing" && (
              <button
                type="button"
                onClick={() => setVoiceNotice(null)}
                className="ms-voice-dismiss-btn"
                title="Dismiss"
                aria-label="Dismiss voice notice"
              >
                ✕
              </button>
            )}
          </div>
        )}

        {/* Curated Prompt Memories for Testability */}
        <div className="ms-curated-section">
          <div className="ms-curated-label">
            <span>Or try a remembered moment:</span>
          </div>
          <div className="ms-curated-grid">
            {CURATED_MEMORIES.map((m) => {
              const isSelected = memoryInput === m.memoryText;
              return (
                <button
                  key={m.id}
                  type="button"
                  className={`ms-curated-chip ${isSelected ? "ms-curated-chip-active" : ""}`}
                  onClick={() => handleSelectCurated(m)}
                  disabled={loading}
                  title={m.hint}
                >
                  <span className="ms-curated-icon">{m.icon}</span>
                  <div className="ms-curated-text">
                    <span className="ms-curated-title">{m.label}</span>
                    <span className="ms-curated-cat">{m.category}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Error Notice */}
      {error && (
        <div className="ms-error-card">
          <AlertCircle size={20} color="#EA4335" />
          <div>
            <strong>Unable to complete memory search:</strong> {error}
            <div style={{ marginTop: "0.25rem", fontSize: "0.8125rem", color: "#FCA5A5" }}>
              Please ensure the backend server is running at <code>{apiBaseUrl}</code>.
            </div>
          </div>
        </div>
      )}

      {/* Experience Stage: AI Interpretation Feedback ("Behind the Scenes" made intuitive) */}
      {response && (
        <>
          <section className="ms-interpretation-card">
            <div className="ms-interpretation-header">
              <div className="ms-interpretation-badge">
                <Sparkles size={14} color="#FBBC05" />
                <span>AI Memory Assistant · Understood Intent</span>
              </div>
              {memorySearchResp?.llm_provider && (
                <span className={`ms-provider-pill ${memorySearchResp.llm_provider === "groq" ? "" : "ms-provider-fallback"}`}>
                  {memorySearchResp.llm_provider === "groq" ? `⚡ Groq NLU (${memorySearchResp.model_name || "Llama 3.3"})` : "⚙️ Fallback NLU"}
                </span>
              )}
              <div className="ms-interpretation-query">
                Remembered: <strong>&ldquo;{response.raw_input}&rdquo;</strong>
              </div>
            </div>

            <div className="ms-interpretation-body">
              {/* Coherent Memory Facets ("You remembered...") */}
              <div className="ms-understanding-hero">
                <div className="ms-you-remember-title">
                  <Sparkles size={14} color="var(--accent-blue)" />
                  <span>You Remembered:</span>
                </div>

                <div className="ms-facets-grid">
                  {/* Occasion / Event */}
                  {structuredClues?.event_activity && (structuredClues.event_activity.event_name || structuredClues.event_activity.activity) && (
                    <div className="ms-facet-card">
                      <div className="ms-facet-header">
                        <span className="ms-facet-label">
                          <Calendar size={13} color="#F472B6" /> Occasion / Event
                        </span>
                        <span className={`ms-certainty-badge ms-certainty-${structuredClues.event_activity.certainty}`}>
                          {structuredClues.event_activity.certainty === "explicit" ? "Stated" : "Inferred"}
                        </span>
                      </div>
                      <div className="ms-facet-value">
                        {[structuredClues.event_activity.event_name, structuredClues.event_activity.activity].filter(Boolean).join(" · ")}
                      </div>
                    </div>
                  )}

                  {/* Place / Location / Setting */}
                  {(structuredClues?.place_location?.place || structuredClues?.scene_environment?.environment) && (
                    <div className="ms-facet-card">
                      <div className="ms-facet-header">
                        <span className="ms-facet-label">
                          <MapPin size={13} color="#34D399" /> Location / Setting
                        </span>
                        <span className={`ms-certainty-badge ms-certainty-${structuredClues?.place_location?.certainty || structuredClues?.scene_environment?.certainty}`}>
                          {(structuredClues?.place_location?.certainty || structuredClues?.scene_environment?.certainty) === "explicit" ? "Stated" : "Inferred"}
                        </span>
                      </div>
                      <div className="ms-facet-value">
                        {structuredClues?.place_location
                          ? [structuredClues.place_location.attributes?.join(" "), structuredClues.place_location.place].filter(Boolean).join(" ")
                          : structuredClues?.scene_environment?.environment}
                      </div>
                    </div>
                  )}

                  {/* Approximate Time */}
                  {structuredClues?.time_temporal?.raw_expression && (
                    <div className="ms-facet-card">
                      <div className="ms-facet-header">
                        <span className="ms-facet-label">
                          <Clock size={13} color="#C084FC" /> Time Anchor
                        </span>
                        <span className={`ms-certainty-badge ms-certainty-${structuredClues.time_temporal.certainty}`}>
                          {structuredClues.time_temporal.certainty === "explicit" ? "Stated" : "Inferred"}
                        </span>
                      </div>
                      <div className="ms-facet-value">
                        {structuredClues.time_temporal.raw_expression}
                      </div>
                    </div>
                  )}

                  {/* Objects & Appearance */}
                  {((structuredClues?.objects && structuredClues.objects.length > 0) || (structuredClues?.visual_attributes && structuredClues.visual_attributes.length > 0)) && (
                    <div className="ms-facet-card">
                      <div className="ms-facet-header">
                        <span className="ms-facet-label">
                          <Tag size={13} color="#FBBF24" /> Objects & Details
                        </span>
                        <span className={`ms-certainty-badge ms-certainty-${structuredClues.objects?.[0]?.certainty || structuredClues.visual_attributes?.[0]?.certainty || "explicit"}`}>
                          {(structuredClues.objects?.[0]?.certainty || structuredClues.visual_attributes?.[0]?.certainty) === "explicit" ? "Stated" : "Inferred"}
                        </span>
                      </div>
                      <div className="ms-facet-value">
                        {[
                          ...(structuredClues.objects || []).map(o => [o.attributes?.join(" "), o.name].filter(Boolean).join(" ")),
                          ...(structuredClues.visual_attributes || []).map(v => v.attribute)
                        ].filter((v, i, a) => a.indexOf(v) === i).join(", ")}
                      </div>
                    </div>
                  )}

                  {/* People / Kinship */}
                  {structuredClues?.people && structuredClues.people.length > 0 && (
                    <div className="ms-facet-card">
                      <div className="ms-facet-header">
                        <span className="ms-facet-label">
                          <Users size={13} color="#60A5FA" /> Who
                        </span>
                        <span className={`ms-certainty-badge ms-certainty-${structuredClues.people[0]?.certainty || "explicit"}`}>
                          {structuredClues.people[0]?.certainty === "explicit" ? "Stated" : "Inferred"}
                        </span>
                      </div>
                      <div className="ms-facet-value">
                        {structuredClues.people.map(p => `${p.count ? `${p.count}× ` : ""}${p.role}${p.attributes?.length ? ` (${p.attributes.join(", ")})` : ""}`).join(", ")}
                      </div>
                    </div>
                  )}

                  {!hasClues && (
                    <div className="ms-facet-card">
                      <div className="ms-facet-value" style={{ fontSize: "0.8125rem", color: "var(--text-muted)" }}>
                        Fuzzy memory mapped through semantic search terms: {response.retrieval_signals.search_query_terms?.join(", ") || "None"}
                      </div>
                    </div>
                  )}
                </div>

                {/* Coherent Natural Language Synthesis */}
                {structuredClues && (
                  <div className="ms-synthesis-box">
                    <strong>Coherent Search Intent:</strong> Searching for moments
                    {structuredClues.people?.length ? <> of <strong>{structuredClues.people.map(p => p.role).join(", ")}</strong></> : null}
                    {structuredClues.event_activity?.event_name ? <> during <strong>{structuredClues.event_activity.event_name}</strong></> : null}
                    {structuredClues.place_location?.place ? <> near <strong>{structuredClues.place_location.place}</strong></> : null}
                    {structuredClues.time_temporal?.raw_expression ? <> ({structuredClues.time_temporal.raw_expression})</> : null}
                    {structuredClues.objects?.length ? <> with <strong>{structuredClues.objects.map(o => [o.attributes?.join(" "), o.name].filter(Boolean).join(" ")).join(", ")}</strong></> : null}.
                  </div>
                )}
              </div>

              {/* Explicit vs Inferred Clues Summary */}
              {structuredClues && ((structuredClues.explicit_clues && structuredClues.explicit_clues.length > 0) || (structuredClues.inferred_clues && structuredClues.inferred_clues.length > 0)) && (
                <div className="ms-clues-summary-box">
                  {structuredClues.explicit_clues && structuredClues.explicit_clues.length > 0 && (
                    <div className="ms-clues-summary-line">
                      <span className="ms-clues-summary-tag ms-tag-explicit-label">Explicit Clues</span>
                      <span style={{ color: "var(--text-primary)" }}>{structuredClues.explicit_clues.join(" · ")}</span>
                    </div>
                  )}
                  {structuredClues.inferred_clues && structuredClues.inferred_clues.length > 0 && (
                    <div className="ms-clues-summary-line">
                      <span className="ms-clues-summary-tag ms-tag-inferred-label">Inferred (Hedged)</span>
                      <span style={{ color: "var(--text-secondary)" }}>{structuredClues.inferred_clues.join(" · ")}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </section>

          {/* Conversational Clarification Block if Memory is Ambiguous */}
          {memorySearchResp?.is_ambiguous && memorySearchResp?.clarification_question && (
            <section className="ms-clarification-card">
              <div className="ms-clarification-header">
                <span className="ms-clarification-badge">
                  <Sparkles size={12} color="#FDE047" />
                  <span>Clarification Question</span>
                </span>
                <span className="ms-clarification-title">To help narrow down the exact moment from similar memories:</span>
              </div>
              <div className="ms-clarification-question">
                &ldquo;{memorySearchResp.clarification_question}&rdquo;
              </div>
              <form onSubmit={handleClarificationSubmit} className="ms-clarification-form">
                <input
                  type="text"
                  className="ms-clarification-input"
                  placeholder="Answer to clarify (e.g. It was 2022 near Baga Beach)..."
                  value={clarificationInput}
                  onChange={(e) => setClarificationInput(e.target.value)}
                  disabled={loading}
                />
                <button
                  type="submit"
                  className="ms-clarification-submit"
                  disabled={loading || !clarificationInput.trim()}
                >
                  Refine Memory →
                </button>
              </form>
            </section>
          )}
        </>
      )}

      {/* Experience Stage: Relevant Results & Recognition */}
      {response && (
        <section className="ms-results-section">
          <div className="ms-results-header">
            <div>
              <h2 className="ms-results-title">
                <BookmarkCheck size={22} color="var(--accent-blue)" />
                <span>Evidence Records Retrieved ({response.results.length} cases)</span>
              </h2>
              <p className="ms-results-subtitle">
                The prototype evaluates retrieval against the 308-record qualitative research archive of Google Photos user search challenges. In production, these signals query your personal photo library.
              </p>
            </div>

            {recognizedIds.size > 0 && (
              <div className="ms-recognized-counter">
                <CheckCircle2 size={16} color="#34D399" />
                <span>{recognizedIds.size} evidence reviewed</span>
              </div>
            )}
          </div>

          {response.results.length === 0 ? (
            <div className="ms-empty-card">
              <Compass size={40} color="#94A3B8" />
              <h3>No matching memory found</h3>
              <p>
                We couldn&apos;t match that specific description in the evidence archive. Try adding a landmark, who was with you, or an object in the photo.
              </p>
              <div className="ms-empty-suggestions">
                {CURATED_MEMORIES.slice(0, 3).map((m) => (
                  <button
                    key={m.id}
                    type="button"
                    className="ms-refine-pill"
                    onClick={() => handleSelectCurated(m)}
                  >
                    Try: &ldquo;{m.memoryText}&rdquo;
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="ms-cards-grid">
              {response.results.map((item: CandidateResult, index: number) => {
                const isRecognized = recognizedIds.has(item.candidate_id);
                const isTopMatch = index === 0;

                // Derive an honest, relatable contextual badge based on data
                let memoryIcon = "📷";
                if (item.content.toLowerCase().includes("ice") || item.content.toLowerCase().includes("snow") || item.content.toLowerCase().includes("mountain")) {
                  memoryIcon = "🏔️";
                } else if (item.content.toLowerCase().includes("sister") || item.content.toLowerCase().includes("friend") || item.content.toLowerCase().includes("family")) {
                  memoryIcon = "👥";
                } else if (item.content.toLowerCase().includes("bike") || item.content.toLowerCase().includes("bicycle")) {
                  memoryIcon = "🚲";
                } else if (item.content.toLowerCase().includes("diya") || item.content.toLowerCase().includes("wedding")) {
                  memoryIcon = "🪔";
                } else if (item.content.toLowerCase().includes("document") || item.content.toLowerCase().includes("paper")) {
                  memoryIcon = "📄";
                }

                return (
                  <div
                    key={item.candidate_id}
                    className={`ms-card ${isRecognized ? "ms-card-recognized" : ""} ${isTopMatch ? "ms-card-top" : ""}`}
                  >
                    {/* Visual Card Header */}
                    <div className="ms-card-header">
                      <div className="ms-card-meta">
                        <span className="ms-card-emoji">{memoryIcon}</span>
                        <div>
                          <div className="ms-card-category">
                            Evidence Case #{item.rank}
                          </div>
                          <div className="ms-card-id">
                            Record ID: {item.candidate_id.slice(0, 8)}...
                          </div>
                        </div>
                      </div>

                      {/* Match Indicator */}
                      <span className={`ms-match-badge ${isTopMatch ? "ms-match-best" : "ms-match-normal"}`}>
                        {isTopMatch ? "Primary Signal Match" : "Signal Match"}
                      </span>
                    </div>

                    {/* Verbatim Content honestly displayed */}
                    <div className="ms-card-content">
                      <p className="ms-card-quote">&ldquo;{item.content}&rdquo;</p>
                    </div>

                    {/* Clue Tags from record */}
                    {item.metadata?.category_tags && Array.isArray(item.metadata.category_tags) && item.metadata.category_tags.length > 0 && (
                      <div className="ms-card-tags">
                        {item.metadata.category_tags.slice(0, 3).map((tag, tIdx) => (
                          <span key={tIdx} className="ms-tag-pill">
                            #{tag}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Recognition Action Bar */}
                    <div className="ms-card-actions">
                      <button
                        type="button"
                        onClick={() => toggleRecognized(item.candidate_id)}
                        className={`ms-recognize-btn ${isRecognized ? "ms-recognized-active" : ""}`}
                      >
                        {isRecognized ? (
                          <>
                            <CheckCircle2 size={16} color="#34D399" />
                            <span>Recognized Memory!</span>
                          </>
                        ) : (
                          <>
                            <Heart size={16} />
                            <span>I recognize this photo memory</span>
                          </>
                        )}
                      </button>

                      {isRecognized && (
                        <span className="ms-recognition-toast">
                          Matched to your timeline
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      )}

      {/* Experience Stage: Conversational Refinement & Retry */}
      {response && (
        <section className="ms-refine-section">
          <div className="ms-refine-header">
            <Sparkles size={18} color="var(--accent-yellow)" />
            <div>
              <h3 className="ms-refine-title">Not quite the photo you remembered?</h3>
              <p className="ms-refine-subtitle">
                Memories are fuzzy and layered. Add another detail to refine the retrieval:
              </p>
            </div>
          </div>

          <div className="ms-refine-chips">
            {REFINEMENT_PROMPTS.map((prompt, idx) => (
              <button
                key={idx}
                type="button"
                className="ms-refine-chip"
                onClick={() => applyRefinement(prompt.text)}
                disabled={loading}
              >
                <span>{prompt.label}</span>
                <ArrowRight size={12} style={{ marginLeft: "4px" }} />
              </button>
            ))}
          </div>
        </section>
      )}

      {/* Product Honesty Notice */}
      <footer className="ms-footer-notice">
        <div className="ms-footer-content">
          <Compass size={16} color="var(--text-muted)" style={{ flexShrink: 0 }} />
          <span>
            <strong>Evaluation Prototype Note:</strong> Memory Search retrieves real qualitative evidence records from your connected corpus to demonstrate natural-language memory retrieval and recognition. In a production Google Photos deployment, these candidates link directly to high-resolution photo assets and timeline albums.
          </span>
        </div>
      </footer>
    </div>
  );
}
