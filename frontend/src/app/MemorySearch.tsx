"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import {
  Search,
  Sparkles,
  Mic,
  RotateCcw,
  CheckCircle2,
  ArrowRight,
  AlertCircle,
  Heart,
  Compass,
  ArrowLeft,
  X,
  Share2,
  FolderPlus,
  HelpCircle,
  Grid,
} from "lucide-react";
import {
  DiscoveryResponse,
  CandidateResult,
  MemorySearchResponse,
} from "../types/discovery";

export type AppScreen =
  | "splash"
  | "photos"
  | "search"
  | "memory-search"
  | "listening"
  | "results"
  | "clarification";

export interface MemorySearchProps {
  currentScreen: "memory-search" | "listening" | "results" | "clarification";
  setCurrentScreen: (screen: AppScreen) => void;
  initialQuery?: string;
  onNavigateBackToSearch: () => void;
}

export type VoiceStatus = "idle" | "listening" | "transcribing" | "unsupported" | "error";

export interface VoiceNotice {
  text: string;
  level: "info" | "listening" | "transcribing" | "success" | "error";
}

const GENERIC_META_STOPWORDS = new Set([
  "photo", "photos", "picture", "pictures", "image", "images", "remember",
  "memory", "memories", "took", "taken", "taking", "look", "looking",
  "search", "show", "find", "nice", "good", "there", "were", "with",
  "from", "about", "that", "this", "some", "our", "my", "me", "i", "we",
  "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of", "was",
]);

const DOCUMENT_TAGS = new Set(["DOCUMENT_SEARCH", "OCR", "RECEIPT_SEARCH"]);
const DOCUMENT_TERMS = ["document", "receipt", "paper", "text", "bill", "invoice", "license", "card"];

function isEligibleAndGroundedCandidate(
  item: CandidateResult,
  queryText: string,
  response: MemorySearchResponse | DiscoveryResponse | null
): boolean {
  const meta = item.metadata || {};

  // 1. Existing consumer eligibility gates
  const evidenceType = String(meta.evidence_type || "").toUpperCase();
  if (evidenceType === "FAILURE" || evidenceType === "PAIN_POINT") return false;

  const tags = Array.isArray(meta.category_tags) ? meta.category_tags : [];
  const upperTags = tags.map((t: string) => String(t).toUpperCase());
  if (upperTags.includes("SEARCH_PROBLEM")) return false;

  const failureMode = meta.failure_mode;
  if (failureMode && !["NONE", "NULL", ""].includes(String(failureMode).toUpperCase())) {
    return false;
  }

  const methodology = String(meta.methodology || "").toUpperCase();
  if (methodology === "UNSOLICITED_PUBLIC") return false;

  // 2. Reject document/OCR search cases unless user explicitly asks for documents
  const lowerQuery = queryText.toLowerCase();
  const isDocQuery = DOCUMENT_TERMS.some((term) => lowerQuery.includes(term));
  if (!isDocQuery && upperTags.some((t) => DOCUMENT_TAGS.has(t))) {
    return false;
  }

  // Baseline eligibility
  const isEligible =
    evidenceType === "SUCCESS" ||
    methodology === "PROMPTED_INTERVIEW" ||
    ["PHOTO_ARCHIVE", "USER_INTERVIEW"].includes(
      String(
        (meta as Record<string, unknown>).source ||
        (meta as Record<string, unknown>).source_type ||
        ""
      ).toUpperCase()
    ) ||
    (!evidenceType && !methodology && !failureMode);

  if (!isEligible) return false;

  // 3. Bound entity bonus check: candidates with bound_bonus > 0 are strongly grounded
  const boundBonus = item.score_breakdown?.bound_bonus ?? 0;
  if (boundBonus > 0) return true;

  // 4. For bound_bonus <= 0, require at least one salient structured clue overlap
  const salientTokens = new Set<string>();

  const memoryResp =
    response && "structured_clues" in response
      ? (response as MemorySearchResponse)
      : null;
  const structuredClues = memoryResp?.structured_clues;
  const v2Frame = response?.v2_frame;

  if (structuredClues) {
    structuredClues.people?.forEach((p) => {
      if (p.role) p.role.toLowerCase().split(/\s+/).forEach((w) => salientTokens.add(w));
    });
    structuredClues.objects?.forEach((o) => {
      if (o.name) o.name.toLowerCase().split(/\s+/).forEach((w) => salientTokens.add(w));
      o.attributes?.forEach((a) => a.toLowerCase().split(/\s+/).forEach((w) => salientTokens.add(w)));
    });
    if (structuredClues.event_activity?.event_name) {
      structuredClues.event_activity.event_name.toLowerCase().split(/\s+/).forEach((w) => salientTokens.add(w));
    }
    if (structuredClues.event_activity?.activity) {
      structuredClues.event_activity.activity.toLowerCase().split(/\s+/).forEach((w) => salientTokens.add(w));
    }
    if (structuredClues.place_location?.place) {
      structuredClues.place_location.place.toLowerCase().split(/\s+/).forEach((w) => salientTokens.add(w));
    }
    structuredClues.visual_attributes?.forEach((v) => {
      if (v.attribute) v.attribute.toLowerCase().split(/\s+/).forEach((w) => salientTokens.add(w));
    });
  }

  if (v2Frame) {
    v2Frame.people?.forEach((p) => {
      if (p.role) p.role.toLowerCase().split(/\s+/).forEach((w) => salientTokens.add(w));
    });
    v2Frame.objects?.forEach((o) => {
      if (o.name) o.name.toLowerCase().split(/\s+/).forEach((w) => salientTokens.add(w));
    });
    if (v2Frame.spatial_setting) {
      v2Frame.spatial_setting.toLowerCase().split(/\s+/).forEach((w) => salientTokens.add(w));
    }
    if (v2Frame.events?.event_name) {
      v2Frame.events.event_name.toLowerCase().split(/\s+/).forEach((w) => salientTokens.add(w));
    }
  }

  // Filter out generic meta stopwords
  const filteredTokens = Array.from(salientTokens).filter(
    (w) => w.length > 2 && !GENERIC_META_STOPWORDS.has(w)
  );

  if (filteredTokens.length > 0) {
    const candidateText = `${item.content || ""} ${upperTags.join(" ")}`.toLowerCase();
    const hasOverlap = filteredTokens.some((token) => candidateText.includes(token));
    if (!hasOverlap) return false;
  }

  return true;
}

export default function MemorySearch({
  currentScreen,
  setCurrentScreen,
  initialQuery,
  onNavigateBackToSearch,
}: MemorySearchProps) {
  const [memoryInput, setMemoryInput] = useState<string>(initialQuery || "");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<MemorySearchResponse | DiscoveryResponse | null>(null);
  const [clarificationInput, setClarificationInput] = useState<string>("");
  const [recognizedIds, setRecognizedIds] = useState<Set<string>>(new Set());

  // MediaRecorder audio capture state
  const [voiceStatus, setVoiceStatus] = useState<VoiceStatus>("idle");
  const [voiceNotice, setVoiceNotice] = useState<VoiceNotice | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const mediaStreamRef = useRef<MediaStream | null>(null);

  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL || "https://google-photos-mvp-production.up.railway.app";

  // Check MediaRecorder capability on client mount and ensure microphone cleanup on unmount
  useEffect(() => {
    if (typeof window !== "undefined") {
      if (!navigator?.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
        setVoiceStatus("unsupported");
      }
    }
    return () => {
      // Ensure microphone stream is stopped if component unmounts while listening
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((track) => track.stop());
        mediaStreamRef.current = null;
      }
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
        try {
          mediaRecorderRef.current.stop();
        } catch {}
      }
    };
  }, []);

  const [refinementCount, setRefinementCount] = useState<number>(0);

  const executeMemorySearch = useCallback(
    async (queryText: string, isRefinement = false) => {
      const cleanText = queryText.trim();
      if (!cleanText) return;

      setLoading(true);
      setError(null);

      try {
        const res = await fetch(`${apiBaseUrl}/api/v1/memory/search`, {
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

        if (!res.ok) {
          let errorDetail = `Service error (${res.status})`;
          try {
            const errData = await res.json();
            if (errData?.detail) {
              errorDetail = typeof errData.detail === "string" ? errData.detail : JSON.stringify(errData.detail);
            }
          } catch {}
          throw new Error(errorDetail);
        }

        const data: MemorySearchResponse | DiscoveryResponse = await res.json();
        setResponse(data);

        // CONDITIONAL ROUTING: Ambiguity -> Screen 7 (Clarification) vs Clear -> Screen 6 (Results)
        // If user already answered clarification (isRefinement = true or refinementCount > 0), proceed to results to avoid infinite loop
        const isAmbiguous = "is_ambiguous" in data && Boolean(data.is_ambiguous) && Boolean(data.clarification_question);
        if (isAmbiguous && !isRefinement && refinementCount === 0) {
          setCurrentScreen("clarification");
        } else {
          setCurrentScreen("results");
        }
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Unable to retrieve memories right now.";
        setError(msg);
      } finally {
        setLoading(false);
      }
    },
    [apiBaseUrl, setCurrentScreen, refinementCount]
  );

  // Sync initialQuery if changed from parent
  useEffect(() => {
    if (initialQuery && initialQuery.trim()) {
      setMemoryInput(initialQuery);
    }
  }, [initialQuery]);

  // Voice recording starter
  const startListening = async () => {
    if (typeof window === "undefined") return;

    if (voiceStatus === "unsupported") {
      setVoiceNotice({
        text: "Audio recording is not supported in this browser. You can type your memory instead.",
        level: "info",
      });
      return;
    }

    try {
      if (!navigator?.mediaDevices?.getUserMedia) {
        setVoiceStatus("unsupported");
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

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
        if (mediaStreamRef.current) {
          mediaStreamRef.current.getTracks().forEach((track) => track.stop());
          mediaStreamRef.current = null;
        }

        const chunks = audioChunksRef.current;
        if (!chunks || chunks.length === 0) {
          setVoiceStatus("error");
          setVoiceNotice({
            text: "No audio was captured. Please try speaking again.",
            level: "error",
          });
          setCurrentScreen("memory-search");
          return;
        }

        const mime = recorder.mimeType || chosenMime || "audio/webm";
        const audioBlob = new Blob(chunks, { type: mime });

        setVoiceStatus("transcribing");
        setVoiceNotice({
          text: "Transcribing your memory...",
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
              text: "No speech recognized. Please speak clearly and try again.",
              level: "error",
            });
            setCurrentScreen("memory-search");
            return;
          }

          // POPULATE MEMORY INPUT WITHOUT AUTO-SEARCHING (Requirement 6)
          setMemoryInput(text);
          setVoiceStatus("idle");
          setVoiceNotice(null);
          // Return to Screen 4 so user can review/edit before clicking Find Memory
          setCurrentScreen("memory-search");
        } catch (err: unknown) {
          setVoiceStatus("error");
          const msg = err instanceof Error ? err.message : "Failed to transcribe audio.";
          setVoiceNotice({
            text: msg,
            level: "error",
          });
          setCurrentScreen("memory-search");
        }
      };

      recorder.start();
      setVoiceStatus("listening");
      setCurrentScreen("listening");
    } catch {
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((track) => track.stop());
        mediaStreamRef.current = null;
      }
      setVoiceStatus("error");
    }
  };

  // Stop speaking action (RED BUTTON)
  const stopListening = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      try {
        mediaRecorderRef.current.stop();
      } catch {}
    }
  };

  // Cancel listening action (BLUE BUTTON)
  const cancelListening = () => {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      try {
        mediaRecorderRef.current.stop();
      } catch {}
    }
    audioChunksRef.current = [];
    setVoiceStatus("idle");
    setVoiceNotice(null);
    setCurrentScreen("memory-search");
  };

  const handleSearchSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (loading || voiceStatus === "transcribing" || voiceStatus === "listening") return;
    setRefinementCount(0);
    executeMemorySearch(memoryInput, false);
  };

  const handleClarificationSubmit = (answer: string) => {
    if (!answer.trim() || loading) return;
    const refined = `${memoryInput.trim()}, ${answer.trim()}`;
    setMemoryInput(refined);
    setClarificationInput("");
    setRefinementCount((prev) => prev + 1);
    executeMemorySearch(refined, true);
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

  // Extract structured clues safely
  const memorySearchResp = response && "structured_clues" in response ? (response as MemorySearchResponse) : null;
  const structuredClues = memorySearchResp?.structured_clues;

  // Build facet chip items dynamically from actual backend response
  const facetChips: { label: string; icon: string }[] = [];
  if (structuredClues) {
    if (structuredClues.people && structuredClues.people.length > 0) {
      structuredClues.people.forEach((p) => {
        facetChips.push({
          label: `${p.count ? `${p.count}× ` : ""}${p.role}${p.attributes?.length ? ` (${p.attributes.join(", ")})` : ""}`,
          icon: "👥",
        });
      });
    }
    if (structuredClues.place_location?.place) {
      facetChips.push({ label: structuredClues.place_location.place, icon: "🏖️" });
    }
    if (structuredClues.event_activity?.event_name || structuredClues.event_activity?.activity) {
      const ev = [structuredClues.event_activity.event_name, structuredClues.event_activity.activity].filter(Boolean).join(" · ");
      facetChips.push({ label: ev, icon: "🌅" });
    }
    if (structuredClues.objects && structuredClues.objects.length > 0) {
      structuredClues.objects.forEach((o) => {
        const fullObj = [o.attributes?.join(" "), o.name].filter(Boolean).join(" ");
        facetChips.push({ label: fullObj, icon: "🚲" });
      });
    }
    if (structuredClues.time_temporal?.raw_expression) {
      facetChips.push({ label: structuredClues.time_temporal.raw_expression, icon: "⏳" });
    }
  } else if (response?.v2_frame) {
    const f = response.v2_frame;
    f.people?.forEach((p) => facetChips.push({ label: p.role, icon: "👥" }));
    if (f.spatial_setting) facetChips.push({ label: f.spatial_setting, icon: "🏖️" });
    f.objects?.forEach((o) => facetChips.push({ label: o.name, icon: "🚲" }));
    if (f.events?.event_name) facetChips.push({ label: f.events.event_name, icon: "🌅" });
  }

  // =========================================================================
  // SCREEN 5: VOICE LISTENING SCREEN
  // =========================================================================
  if (currentScreen === "listening") {
    return (
      <div className="gp-screen-container">
        {/* Top Header */}
        <div className="gp-screen-header">
          <button
            type="button"
            className="gp-header-back-btn"
            onClick={cancelListening}
            title="Cancel and return"
          >
            <ArrowLeft size={20} color="#202124" />
          </button>
          <h2 className="gp-header-title">Memory Search</h2>
          <div className="gp-header-avatar">
            <span>K</span>
          </div>
        </div>

        {/* AI SEARCH Sub-badge */}
        <div className="gp-ai-sub-badge">
          <Sparkles size={14} color="#1A73E8" />
          <span>AI SEARCH · Natural Memory Recall</span>
        </div>

        {/* Central Listening Card */}
        <div className="gp-voice-card">
          <h3 className="gp-voice-title">
            {voiceStatus === "transcribing" ? "Transcribing memory..." : "Listening..."}
          </h3>
          <p className="gp-voice-subtitle">
            {voiceStatus === "transcribing"
              ? "Converting your speech into natural memory clues..."
              : "Tell me what you remember about the photo."}
          </p>

          {/* Animated Pulsing Mic Circle */}
          <div className="gp-voice-mic-container">
            {voiceStatus === "listening" && <div className="gp-listening-pulse" />}
            <div className={`gp-voice-mic-circle ${voiceStatus === "listening" ? "active" : ""}`}>
              {voiceStatus === "transcribing" ? (
                <RotateCcw size={32} className="gp-spin" color="#1A73E8" />
              ) : (
                <Mic size={36} color="#1A73E8" />
              )}
            </div>
          </div>

          <div className="gp-voice-cue">
            <span>👂 &ldquo;listening for people, places, or moments...&rdquo;</span>
          </div>

          {/* TWO VISUALLY DISTINCT BUTTONS: Strong RED Stop vs BLUE Cancel */}
          <div className="gp-voice-actions">
            <button
              type="button"
              className="gp-btn-stop-speaking"
              onClick={stopListening}
              disabled={voiceStatus === "transcribing"}
            >
              <span>■ Stop Speaking</span>
            </button>

            <button
              type="button"
              className="gp-btn-cancel-listening"
              onClick={cancelListening}
            >
              <span>Cancel</span>
            </button>
          </div>
        </div>

        {/* Helper Card Below */}
        <div className="gp-voice-helper-card">
          <div className="gp-helper-header">
            <span className="gp-helper-bulb">💡</span>
            <span className="gp-helper-title">Speak freely and naturally</span>
          </div>
          <p className="gp-helper-desc">
            Describe the moment as you recall it — who was there, an item, the location, or how the light felt.
          </p>
          <div className="gp-helper-examples">
            <div className="gp-helper-example-item">
              <span>🚲</span>
              <span>&ldquo;shadi me bhai ke saath white bike ...&rdquo;</span>
            </div>
            <div className="gp-helper-example-item">
              <span>🌅</span>
              <span>&ldquo;with family we went to a view point ..&rdquo;</span>
            </div>
            <div className="gp-helper-example-item">
              <span>🏔️</span>
              <span>&ldquo;hiking trip aur wo foggy mountains..&rdquo;</span>
            </div>
          </div>
        </div>

        {/* Footer Language & Privacy Info */}
        <div className="gp-voice-footer">
          <div className="gp-lang-pill-row">
            <span>🌐 Search in English, Hindi &amp; Hinglish</span>
            <span className="gp-auto-badge">Auto</span>
          </div>
          <p className="gp-privacy-note">
            Your search requests stay private and protected by Google Photos.
          </p>
        </div>
      </div>
    );
  }

  // =========================================================================
  // SCREEN 7: CLARIFICATION SCREEN (CONDITIONAL ONLY)
  // =========================================================================
  if (currentScreen === "clarification" && memorySearchResp?.clarification_question) {
    return (
      <div className="gp-screen-container">
        {/* Top Header */}
        <div className="gp-screen-header">
          <button
            type="button"
            className="gp-header-back-btn"
            onClick={() => setCurrentScreen("memory-search")}
            title="Back to search input"
          >
            <ArrowLeft size={20} color="#202124" />
          </button>
          <h2 className="gp-header-title">Memory Search</h2>
          <div className="gp-header-avatar">
            <span>K</span>
          </div>
        </div>

        {/* Top Query Pill Bar */}
        <div className="gp-results-query-bar">
          <span className="gp-query-bar-text">&ldquo;{memoryInput}&rdquo;</span>
          <button
            type="button"
            className="gp-query-bar-btn"
            onClick={() => setCurrentScreen("memory-search")}
            title="Edit memory"
          >
            <X size={16} />
          </button>
        </div>

        {/* Memory Assistant Conversational Card */}
        <div className="gp-clarification-card">
          <div className="gp-clarification-card-header">
            <div className="gp-card-badge-row">
              <Sparkles size={16} color="#1A73E8" />
              <span className="gp-card-badge-title">Memory Assistant</span>
            </div>
            <span className="gp-card-badge-count">
              {response?.results ? `${response.results.length} candidate moments` : "3 candidates"}
            </span>
          </div>

          <p className="gp-clarification-intro">
            I found a few moments that could match. Help me narrow down the exact moment:
          </p>

          <div className="gp-clarification-question-box">
            <HelpCircle size={20} color="#1A73E8" style={{ flexShrink: 0 }} />
            <span className="gp-clarification-question-text">
              {memorySearchResp.clarification_question}
            </span>
          </div>

          {/* Quick Option Cards for Tap Selection */}
          <div className="gp-clarification-options">
            <button
              type="button"
              className="gp-clarification-option-btn"
              onClick={() => handleClarificationSubmit("near the beach in Goa")}
              disabled={loading}
            >
              <span className="gp-option-icon">☀️</span>
              <div className="gp-option-text">
                <span className="gp-option-title">Beach / Coast</span>
                <span className="gp-option-sub">Goa coastal trip</span>
              </div>
              <ArrowRight size={16} color="#5F6368" />
            </button>

            <button
              type="button"
              className="gp-clarification-option-btn"
              onClick={() => handleClarificationSubmit("in the mountains in snow")}
              disabled={loading}
            >
              <span className="gp-option-icon">🏔️</span>
              <div className="gp-option-text">
                <span className="gp-option-title">Mountains / Snow</span>
                <span className="gp-option-sub">Rohtang / Himachal trek</span>
              </div>
              <ArrowRight size={16} color="#5F6368" />
            </button>
          </div>

          {/* Text Clarification Form */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleClarificationSubmit(clarificationInput);
            }}
            className="gp-clarification-form"
          >
            <input
              type="text"
              className="gp-clarification-input"
              value={clarificationInput}
              onChange={(e) => setClarificationInput(e.target.value)}
              placeholder="Or type a clarifying detail (e.g. November 2023)..."
              disabled={loading}
            />
            <button
              type="submit"
              className="gp-clarification-submit-btn"
              disabled={loading || !clarificationInput.trim()}
            >
              {loading ? "Narrowing..." : "Refine Memory →"}
            </button>
          </form>
        </div>

        {/* Candidate Moments Preview */}
        {response?.results && response.results.length > 0 && (
          <div className="gp-candidate-preview-section">
            <div className="gp-section-subhead">
              <span>Candidate Memories</span>
              <span style={{ fontSize: "0.8rem", color: "#5F6368" }}>Why we asked</span>
            </div>
            <div className="gp-candidate-grid">
              {response.results
                .filter((item) => isEligibleAndGroundedCandidate(item, memoryInput, response))
                .slice(0, 2)
                .map((item, idx) => (
                  <div key={item.candidate_id || idx} className="gp-candidate-card">
                    <div className="gp-candidate-card-header">
                      <span className="gp-candidate-tag">Candidate #{idx + 1}</span>
                    </div>
                    <p className="gp-candidate-snippet">&ldquo;{item.content}&rdquo;</p>
                  </div>
                ))}
            </div>
          </div>
        )}

        <div className="gp-voice-footer">
          <p className="gp-privacy-note">
            Your search requests stay private and protected by Google Photos.
          </p>
        </div>
      </div>
    );
  }

  // =========================================================================
  // SCREEN 6: RESULTS SCREEN
  // =========================================================================
  if (currentScreen === "results" && response) {
    // Consumer-facing candidate filtering: include only genuine photo memories / successful retrieval episodes
    const candidates = (response.results || []).filter((item: CandidateResult) =>
      isEligibleAndGroundedCandidate(item, memoryInput, response)
    );
    const resultsCount = candidates.length;

    return (
      <div className="gp-screen-container">
        {/* Top Header */}
        <div className="gp-screen-header">
          <button
            type="button"
            className="gp-header-back-btn"
            onClick={() => setCurrentScreen("memory-search")}
            title="Return to memory input"
          >
            <ArrowLeft size={20} color="#202124" />
          </button>
          <h2 className="gp-header-title">Memory Search</h2>
          <div className="gp-header-avatar">
            <span>K</span>
          </div>
        </div>

        {/* Active Query Pill Bar */}
        <div
          className="gp-results-query-bar"
          onClick={() => setCurrentScreen("memory-search")}
          role="button"
          tabIndex={0}
        >
          <Search size={16} color="#5F6368" />
          <span className="gp-query-bar-text">&ldquo;{memoryInput}&rdquo;</span>
          <button
            type="button"
            className="gp-query-bar-btn"
            onClick={(e) => {
              e.stopPropagation();
              setMemoryInput("");
              setCurrentScreen("memory-search");
            }}
            title="Clear query"
          >
            <X size={15} />
          </button>
          <button
            type="button"
            className="gp-query-bar-btn"
            onClick={(e) => {
              e.stopPropagation();
              startListening();
            }}
            title="Speak again"
          >
            <Mic size={15} color="#1A73E8" />
          </button>
        </div>

        {/* "✦ You remembered" AI Intent Understanding Card */}
        <div className="gp-remembered-card">
          <div className="gp-remembered-header">
            <div className="gp-card-badge-row">
              <Sparkles size={16} color="#1A73E8" />
              <span className="gp-remembered-title">You remembered</span>
            </div>
            <span className="gp-remembered-matches">{resultsCount} matches</span>
          </div>

          {/* Structured Clues Facet Chips */}
          <div className="gp-facet-chips-row">
            {facetChips.length > 0 ? (
              facetChips.map((chip, idx) => (
                <span key={idx} className="gp-facet-chip">
                  <span style={{ marginRight: "4px" }}>{chip.icon}</span>
                  {chip.label}
                </span>
              ))
            ) : (
              <span className="gp-facet-chip">
                <span>🔍</span> Natural memory query
              </span>
            )}
          </div>

          <p className="gp-remembered-summary">
            Found {resultsCount} moments matching your description across your photo archive.
          </p>
        </div>

        {/* Filter Pills Row */}
        <div className="gp-results-filter-row">
          <button type="button" className="gp-filter-pill active">
            ✓ All moments ({resultsCount})
          </button>
          <button type="button" className="gp-filter-pill">
            Sunset highlights
          </button>
          <button type="button" className="gp-filter-pill">
            With family
          </button>
        </div>

        {/* "Moments that match" Photo Cards Section */}
        <div className="gp-results-section">
          <div className="gp-results-section-header">
            <span className="gp-results-section-title">Moments that match</span>
            <Grid size={16} color="#5F6368" />
          </div>

          {resultsCount === 0 ? (
            <div className="gp-results-empty-state">
              <Compass size={36} color="#9AA0A6" />
              <h4>No matching moments found</h4>
              <p>Try adding a person, landmark, or memorable detail.</p>
              <button
                type="button"
                className="gp-empty-retry-btn"
                onClick={() => setCurrentScreen("memory-search")}
              >
                Refine Memory Description
              </button>
            </div>
          ) : (
            <div className="gp-results-cards-list">
              {candidates.map((item: CandidateResult, index: number) => {
                const isRecognized = recognizedIds.has(item.candidate_id);
                const isTopMatch = index === 0;
                const displayRank = index + 1;

                // Consumer-facing tags: filter out internal research diagnostics
                const rawTags = Array.isArray(item.metadata?.category_tags)
                  ? (item.metadata.category_tags as string[])
                  : [];
                const consumerTags = rawTags
                  .filter((tag): tag is string => typeof tag === "string")
                  .filter((tag) => {
                    const upper = tag.toUpperCase();
                    return (
                      !upper.includes("SEARCH_") &&
                      !upper.includes("RETRIEVAL") &&
                      !upper.includes("FAILURE") &&
                      !upper.includes("SUCCESS") &&
                      !upper.includes("PROBLEM") &&
                      !upper.includes("ACCURACY") &&
                      !upper.includes("RELEVANCE") &&
                      !upper.includes("PAIN_POINT")
                    );
                  });

                return (
                  <div
                    key={item.candidate_id || index}
                    className={`gp-result-card ${isRecognized ? "recognized" : ""}`}
                  >
                    <div className="gp-result-card-header">
                      <div className="gp-result-meta-line">
                        <span className="gp-result-rank">Moment #{displayRank}</span>
                      </div>
                      <span className={`gp-result-badge ${isTopMatch ? "primary" : ""}`}>
                        {isTopMatch ? "Primary Match" : "Match"}
                      </span>
                    </div>

                    <p className="gp-result-quote">&ldquo;{item.content}&rdquo;</p>

                    {consumerTags.length > 0 && (
                      <div className="gp-result-tags">
                        {consumerTags.slice(0, 3).map((tag, tIdx) => (
                          <span key={tIdx} className="gp-tag-pill">
                            #{tag.toLowerCase().replace(/_/g, " ")}
                          </span>
                        ))}
                      </div>
                    )}

                    <div className="gp-result-card-actions">
                      <button
                        type="button"
                        className={`gp-recognize-btn ${isRecognized ? "active" : ""}`}
                        onClick={() => toggleRecognized(item.candidate_id)}
                      >
                        {isRecognized ? (
                          <>
                            <CheckCircle2 size={16} color="#34A853" />
                            <span>Recognized Memory!</span>
                          </>
                        ) : (
                          <>
                            <Heart size={16} color="#5F6368" />
                            <span>I recognize this photo memory</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Floating Bottom Action Bar */}
        <div className="gp-results-floating-bar">
          <button type="button" className="gp-floating-action-btn">
            <FolderPlus size={16} />
            <span>Create album</span>
          </button>
          <button type="button" className="gp-floating-action-btn">
            <Share2 size={16} />
            <span>Share</span>
          </button>
        </div>
      </div>
    );
  }

  // =========================================================================
  // SCREEN 4: MEMORY SEARCH LANDING SCREEN
  // =========================================================================
  return (
    <div className="gp-screen-container">
      {/* Top Header */}
      <div className="gp-screen-header">
        <button
          type="button"
          className="gp-header-back-btn"
          onClick={onNavigateBackToSearch}
          title="Back to Search Hub"
        >
          <ArrowLeft size={20} color="#202124" />
        </button>
        <h2 className="gp-header-title">Memory Search</h2>
        <div className="gp-header-avatar">
          <span>K</span>
        </div>
      </div>

      {/* Deep Navy Blue Hero Card */}
      <div className="gp-memory-hero-card">
        <div className="gp-hero-badge-pill">
          <Sparkles size={14} color="#FDE047" />
          <span>AI SEARCH · Natural Memory Recall</span>
        </div>

        <h1 className="gp-hero-title">Search by memory, not keywords.</h1>
        <p className="gp-hero-sub">
          Tell us what you remember. You can type it or speak naturally.
        </p>
        <div className="gp-hero-check-row">
          <CheckCircle2 size={15} color="#34D399" />
          <span>No exact dates, tags, or file names needed.</span>
        </div>

        {/* Inner White Input Box */}
        <div className="gp-inner-input-card">
          <div className="gp-inner-card-sub">
            <span style={{ fontSize: "0.8rem", color: "#1A73E8" }}>💬</span>
            <span style={{ fontSize: "0.75rem", fontWeight: 600, color: "#5F6368" }}>Memory Prompt</span>
          </div>

          <h3 className="gp-inner-card-title">What do you remember?</h3>

          <form onSubmit={handleSearchSubmit}>
            <div className="gp-input-wrapper">
              <input
                type="text"
                className="gp-memory-input-field"
                value={memoryInput}
                onChange={(e) => setMemoryInput(e.target.value)}
                placeholder="💡 &ldquo;I remember a family trip near the beach...&rdquo;"
                disabled={loading}
              />
              {memoryInput && (
                <button
                  type="button"
                  className="gp-input-clear-btn"
                  onClick={() => setMemoryInput("")}
                  title="Clear input"
                >
                  <X size={16} />
                </button>
              )}
            </div>

            {/* Two Action Buttons: Speak naturally vs Search */}
            <div className="gp-hero-actions-row">
              <button
                type="button"
                className="gp-btn-speak-naturally"
                onClick={startListening}
                disabled={loading}
              >
                <Mic size={18} color="#1A73E8" />
                <span>Speak naturally</span>
              </button>

              <button
                type="submit"
                className="gp-btn-search-primary"
                disabled={loading || !memoryInput.trim()}
              >
                {loading ? (
                  <>
                    <RotateCcw size={16} className="gp-spin" />
                    <span>Searching...</span>
                  </>
                ) : (
                  <>
                    <span>Search</span>
                    <ArrowRight size={16} />
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Error Notice */}
      {error && (
        <div className="gp-error-banner">
          <AlertCircle size={18} color="#EA4335" />
          <span>{error}</span>
        </div>
      )}

      {/* Voice Notification Banner */}
      {voiceNotice && (
        <div className={`gp-notice-banner ${voiceNotice.level}`}>
          <span>{voiceNotice.text}</span>
          <button type="button" onClick={() => setVoiceNotice(null)} className="gp-notice-close">
            <X size={14} />
          </button>
        </div>
      )}

      {/* "Try describing a memory" Section */}
      <div className="gp-memory-discovery-section">
        <div className="gp-discovery-header">
          <span className="gp-discovery-title">Try describing a memory</span>
          <span className="gp-discovery-hint">Tap to test</span>
        </div>

        <div className="gp-discovery-chips-list">
          <button
            type="button"
            className="gp-discovery-chip-card"
            onClick={() => setMemoryInput("shadi me photo lee thi bhai ki safed bike par")}
          >
            <span className="gp-discovery-icon">🚲</span>
            <div className="gp-discovery-content">
              <div className="gp-discovery-tag-row">
                <span className="gp-tag-hinglish">Hinglish</span>
                <span className="gp-tag-category">Wedding · Bike</span>
              </div>
              <span className="gp-discovery-text">&ldquo;shadi me photo lee thi bhai ki safed bike par&rdquo;</span>
            </div>
            <ArrowRight size={16} color="#9AA0A6" className="gp-chip-arrow" />
          </button>

          <button
            type="button"
            className="gp-discovery-chip-card"
            onClick={() => setMemoryInput("family trip near the beach at sunset")}
          >
            <span className="gp-discovery-icon">🌅</span>
            <div className="gp-discovery-content">
              <div className="gp-discovery-tag-row">
                <span className="gp-tag-travel">Travel</span>
                <span className="gp-tag-category">Coastline · Golden hour</span>
              </div>
              <span className="gp-discovery-text">&ldquo;family trip near the beach at sunset&rdquo;</span>
            </div>
            <ArrowRight size={16} color="#9AA0A6" className="gp-chip-arrow" />
          </button>

          <button
            type="button"
            className="gp-discovery-chip-card"
            onClick={() => setMemoryInput("me and my friends at the mountain in the snow")}
          >
            <span className="gp-discovery-icon">🏔️</span>
            <div className="gp-discovery-content">
              <div className="gp-discovery-tag-row">
                <span className="gp-tag-friends">Friends</span>
                <span className="gp-tag-category">Hiking · Outdoors</span>
              </div>
              <span className="gp-discovery-text">&ldquo;me and my friends at the mountain in the snow&rdquo;</span>
            </div>
            <ArrowRight size={16} color="#9AA0A6" className="gp-chip-arrow" />
          </button>
        </div>
      </div>

      {/* "Recent rediscoveries" Section */}
      <div className="gp-rediscoveries-section">
        <div className="gp-discovery-header">
          <span className="gp-discovery-title">Recent rediscoveries</span>
          <span className="gp-discovery-hint">Your library</span>
        </div>

        <div className="gp-rediscoveries-row">
          <div
            className="gp-rediscovery-card"
            style={{
              backgroundImage: "linear-gradient(180deg, rgba(0,0,0,0) 45%, rgba(0,0,0,0.7) 100%), url('/images/recent/sunset-trip.jpg')",
              backgroundSize: "cover",
              backgroundPosition: "center",
            }}
            onClick={() => setMemoryInput("family trip near the beach at sunset")}
            role="button"
            tabIndex={0}
          >
            <span className="gp-rediscovery-label">Sunset Trip</span>
          </div>

          <div
            className="gp-rediscovery-card"
            style={{
              backgroundImage: "linear-gradient(180deg, rgba(0,0,0,0) 45%, rgba(0,0,0,0.7) 100%), url('/images/recent/white-bike.jpg')",
              backgroundSize: "cover",
              backgroundPosition: "center",
            }}
            onClick={() => setMemoryInput("a picture with that white bike")}
            role="button"
            tabIndex={0}
          >
            <span className="gp-rediscovery-label">White Bike</span>
          </div>

          <div
            className="gp-rediscovery-card"
            style={{
              backgroundImage: "linear-gradient(180deg, rgba(0,0,0,0) 45%, rgba(0,0,0,0.7) 100%), url('/images/recent/mountain-trek.jpg')",
              backgroundSize: "cover",
              backgroundPosition: "center",
            }}
            onClick={() => setMemoryInput("me and my friends at the mountain in the snow")}
            role="button"
            tabIndex={0}
          >
            <span className="gp-rediscovery-label">Mountain Trek</span>
          </div>
        </div>
      </div>

      {/* Footer Banner */}
      <div className="gp-memory-footer">
        <div className="gp-lang-pill-row">
          <span>🛡️ Search in any language you speak — English, Hindi and Hinglish.</span>
        </div>
        <p className="gp-privacy-note">
          Your search requests stay private and protected by Google Photos.
        </p>
      </div>
    </div>
  );
}
