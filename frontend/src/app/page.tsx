"use client";

import { useState, useEffect } from "react";
import MemorySearch, { AppScreen } from "./MemorySearch";
import DiscoveryEngineConsole from "./DiscoveryEngineConsole";
import {
  Search,
  ArrowLeft,
  Clock,
  ChevronRight,
  MoreHorizontal,
  Share2,
} from "lucide-react";

function MemorySearchIcon() {
  return (
    <svg
      width="28"
      height="28"
      viewBox="0 0 28 28"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="gp-card-lens-icon"
    >
      {/* Sparkles */}
      <path d="M5 6L6 3L7 6L10 7L7 8L6 11L5 8L2 7L5 6Z" fill="#F43F5E" />
      <path d="M22 6L23 3.5L24 6L26.5 7L24 8L23 10.5L22 8L19.5 7L22 6Z" fill="#F59E0B" />
      <path d="M4 21L4.8 19L5.6 21L7.6 21.8L5.6 22.6L4.8 24.6L4 22.6L2 21.8L4 21Z" fill="#06B6D4" />
      {/* Lens body */}
      <circle cx="13" cy="13" r="7.5" stroke="url(#lensGrad)" strokeWidth="2.5" />
      {/* Aperture ring */}
      <circle cx="13" cy="13" r="4.2" fill="none" stroke="#8B5CF6" strokeWidth="1.2" strokeDasharray="2 1.5" />
      <circle cx="13" cy="13" r="2.2" fill="#8B5CF6" />
      {/* Handle */}
      <path d="M18.5 18.5L24 24" stroke="url(#handleGrad)" strokeWidth="3" strokeLinecap="round" />
      <defs>
        <linearGradient id="lensGrad" x1="5.5" y1="5.5" x2="20.5" y2="20.5" gradientUnits="userSpaceOnUse">
          <stop stopColor="#06B6D4" />
          <stop offset="0.5" stopColor="#8B5CF6" />
          <stop offset="1" stopColor="#EC4899" />
        </linearGradient>
        <linearGradient id="handleGrad" x1="18.5" y1="18.5" x2="24" y2="24" gradientUnits="userSpaceOnUse">
          <stop stopColor="#8B5CF6" />
          <stop offset="1" stopColor="#EC4899" />
        </linearGradient>
      </defs>
    </svg>
  );
}

function GooglePhotosPinwheel({ size = 26, className = "" }: { size?: number; className?: string }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 200 200"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-label="Google Photos"
    >
      {/* Top Petal - Red */}
      <path d="M 100,100 L 100,30 A 35,35 0 0 1 100,100 Z" fill="#EA4335" />
      {/* Left Petal - Yellow */}
      <path d="M 100,100 L 30,100 A 35,35 0 0 1 100,100 Z" fill="#FBBC05" />
      {/* Bottom Petal - Green */}
      <path d="M 100,100 L 100,170 A 35,35 0 0 1 100,100 Z" fill="#34A853" />
      {/* Right Petal - Blue */}
      <path d="M 100,100 L 170,100 A 35,35 0 0 1 100,100 Z" fill="#4285F4" />
    </svg>
  );
}

export default function Home() {
  const [currentScreen, setCurrentScreen] = useState<AppScreen>("splash");
  const [splashFading, setSplashFading] = useState<boolean>(false);
  const [selectedQuery, setSelectedQuery] = useState<string>("");
  const [isEvaluatorMode, setIsEvaluatorMode] = useState<boolean>(false);

  // Splash screen transition timer (2.5s display, 0.4s fade -> photos)
  useEffect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      if (params.get("view") === "evaluator" || params.get("mode") === "evaluator") {
        setIsEvaluatorMode(true);
        setCurrentScreen("photos");
        return;
      }
    }

    const fadeTimer = setTimeout(() => {
      setSplashFading(true);
    }, 2400);

    const transitionTimer = setTimeout(() => {
      setCurrentScreen("photos");
    }, 2800);

    return () => {
      clearTimeout(fadeTimer);
      clearTimeout(transitionTimer);
    };
  }, []);

  const navigateToMemorySearch = (query: string = "") => {
    setSelectedQuery(query);
    setCurrentScreen("memory-search");
  };

  // Evaluator diagnostic mode (gated strictly via explicit ?view=evaluator query param)
  if (isEvaluatorMode) {
    return (
      <main className="container">
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
              <p className="brand-subtitle">Deliverable 1 Evaluator Diagnostic Console (Isolated)</p>
            </div>
          </div>
          <button
            type="button"
            className="gp-back-btn"
            onClick={() => setIsEvaluatorMode(false)}
            style={{ padding: "0.5rem 1rem", fontSize: "0.85rem" }}
          >
            ← Return to Google Photos Consumer App
          </button>
        </header>
        <DiscoveryEngineConsole />
      </main>
    );
  }

  return (
    <div className="gp-app-viewport">
      {/* =================================================================== */}
      {/* SCREEN 1: SPLASH SCREEN (0 to 2.8s)                                */}
      {/* =================================================================== */}
      {currentScreen === "splash" && (
        <div className={`gp-splash-screen ${splashFading ? "fade-out" : ""}`}>
          <div className="gp-splash-content">
            <GooglePhotosPinwheel size={80} className="gp-splash-pinwheel-img" />
            <span className="gp-splash-wordmark">PHOTOS</span>
          </div>
        </div>
      )}

      {/* =================================================================== */}
      {/* SCREEN 2: GOOGLE PHOTOS HOME TIMELINE                              */}
      {/* =================================================================== */}
      {currentScreen === "photos" && (
        <div className="gp-home-screen">
          {/* Top App Bar */}
          <header className="gp-home-appbar">
            <div className="gp-home-brand-row">
              <GooglePhotosPinwheel size={26} className="gp-home-pinwheel-img" />
              <span className="gp-home-brand-text">Google Photos</span>
            </div>

            <div className="gp-home-avatar" title="Account">
              <span>K</span>
            </div>
          </header>

          {/* Main Timeline Scrollable Content */}
          <div className="gp-home-scroll-body">
            {/* "Memories • ☁ Backed up" Story Carousel */}
            <section className="gp-stories-section">
              <div className="gp-stories-header">
                <div className="gp-stories-title-row">
                  <span className="gp-stories-title">Memories</span>
                  <span className="gp-stories-dot">•</span>
                </div>
                <div className="gp-stories-backed-up">
                  <span>☁ Backed up</span>
                </div>
              </div>

              <div className="gp-stories-carousel">
                {/* Story 1 */}
                <div
                  className="gp-story-card"
                  onClick={() => navigateToMemorySearch("trip to the coast with sunset")}
                  role="button"
                  tabIndex={0}
                  style={{
                    backgroundImage: "linear-gradient(180deg, rgba(0,0,0,0.15) 0%, rgba(0,0,0,0) 40%, rgba(0,0,0,0.75) 100%), url('/images/home/coastal-getaway.jpg'), linear-gradient(135deg, #1f4037 0%, #99f2c8 100%)",
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                  }}
                >
                  <span className="gp-story-badge">1 yr ago</span>
                  <span className="gp-story-label">Coastal Getaway</span>
                </div>

                {/* Story 2 */}
                <div
                  className="gp-story-card"
                  onClick={() => navigateToMemorySearch("hiking trail in mountain peaks")}
                  role="button"
                  tabIndex={0}
                  style={{
                    backgroundImage: "linear-gradient(180deg, rgba(0,0,0,0.15) 0%, rgba(0,0,0,0) 40%, rgba(0,0,0,0.75) 100%), url('/images/home/mountain-trail.jpg'), linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%)",
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                  }}
                >
                  <span className="gp-story-badge">Highlights</span>
                  <span className="gp-story-label">Mountain Trail Hike</span>
                </div>

                {/* Story 3 */}
                <div
                  className="gp-story-card"
                  onClick={() => navigateToMemorySearch("sunset near the sea at golden hour")}
                  role="button"
                  tabIndex={0}
                  style={{
                    backgroundImage: "linear-gradient(180deg, rgba(0,0,0,0.15) 0%, rgba(0,0,0,0) 40%, rgba(0,0,0,0.75) 100%), url('/images/home/summer-sunset.jpg'), linear-gradient(135deg, #f12711 0%, #f5af19 100%)",
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                  }}
                >
                  <span className="gp-story-badge">Spotlight</span>
                  <div className="gp-story-date-bubble">
                    <span style={{ fontSize: "6px", lineHeight: "7px" }}>▲</span>
                    <span>Oct</span>
                    <span style={{ fontSize: "6px", lineHeight: "7px" }}>▼</span>
                  </div>
                  <span className="gp-story-label">Summer Sunset</span>
                </div>
              </div>
            </section>

            {/* Timeline: Today */}
            <section className="gp-home-timeline-group">
              <div className="gp-group-header">
                <div>
                  <h3 className="gp-group-title">Today</h3>
                  <span className="gp-group-sub">San Francisco • 4 moments</span>
                </div>
                <MoreHorizontal size={18} color="#5F6368" />
              </div>

              {/* Big Golden Gate hero card */}
              <div
                className="gp-hero-photo-card"
                style={{
                  backgroundImage: "linear-gradient(180deg, rgba(0,0,0,0) 60%, rgba(0,0,0,0.5) 100%), url('/images/home/golden-gate-hero.jpg'), linear-gradient(135deg, #e65c00 0%, #f9d423 100%)",
                  backgroundSize: "cover",
                  backgroundPosition: "center",
                }}
                onClick={() => navigateToMemorySearch("Golden Gate Bridge in morning fog")}
                role="button"
                tabIndex={0}
              >
                <span className="gp-photo-time-pill">☁ 10:42 AM</span>
              </div>

              {/* 2-col photo split */}
              <div className="gp-photo-split-row">
                <div
                  className="gp-split-photo"
                  style={{
                    backgroundImage: "linear-gradient(180deg, rgba(0,0,0,0) 50%, rgba(0,0,0,0.5) 100%), url('/images/home/cafe.jpg'), linear-gradient(135deg, #3e2723 0%, #8d6e63 100%)",
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                  }}
                  onClick={() => navigateToMemorySearch("coffee at cafe")}
                  role="button"
                  tabIndex={0}
                >
                  <span className="gp-split-photo-tag">Cafe</span>
                </div>
                <div
                  className="gp-split-photo"
                  style={{
                    backgroundImage: "url('/images/home/architecture.jpg'), linear-gradient(135deg, #37474f 0%, #78909c 100%)",
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                  }}
                  role="button"
                  tabIndex={0}
                  onClick={() => navigateToMemorySearch("city architecture")}
                >
                  <span className="gp-split-photo-icon">✦</span>
                </div>
              </div>
            </section>

            {/* Timeline: Last Weekend */}
            <section className="gp-home-timeline-group">
              <div className="gp-group-header">
                <div>
                  <h3 className="gp-group-title">Last Weekend</h3>
                  <span className="gp-group-sub">Pacific Coast • Oct 14–15</span>
                </div>
                <Share2 size={18} color="#5F6368" />
              </div>

              {/* 6-Photo Collage */}
              <div className="gp-six-grid-collage">
                <div
                  className="gp-grid-tile"
                  style={{
                    backgroundImage: "url('/images/home/last-weekend-cliff.jpg'), linear-gradient(135deg, #005c97 0%, #363795 100%)",
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                  }}
                  onClick={() => navigateToMemorySearch("coastal sea cliff")}
                  role="button"
                  tabIndex={0}
                />
                <div
                  className="gp-grid-tile"
                  style={{
                    backgroundImage: "url('/images/home/last-weekend-campfire.jpg'), linear-gradient(135deg, #141e30 0%, #243b55 100%)",
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                  }}
                  onClick={() => navigateToMemorySearch("bonfire on the beach at night")}
                  role="button"
                  tabIndex={0}
                >
                  <span className="gp-tile-circle-indicator">○</span>
                </div>
                <div
                  className="gp-grid-tile"
                  style={{
                    backgroundImage: "url('/images/home/last-weekend-arch.jpg'), linear-gradient(135deg, #4b6cb7 0%, #182848 100%)",
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                  }}
                  onClick={() => navigateToMemorySearch("beach with sea rock arch")}
                  role="button"
                  tabIndex={0}
                />
                <div
                  className="gp-grid-tile"
                  style={{
                    backgroundImage: "url('/images/home/last-weekend-car.jpg'), linear-gradient(135deg, #134e5e 0%, #71b280 100%)",
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                  }}
                  onClick={() => navigateToMemorySearch("car road trip along the coast")}
                  role="button"
                  tabIndex={0}
                />
                <div
                  className="gp-grid-tile"
                  style={{
                    backgroundImage: "url('/images/home/last-weekend-foam.jpg'), linear-gradient(135deg, #1d976c 0%, #93f9b9 100%)",
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                  }}
                  onClick={() => navigateToMemorySearch("standing near sea foam waves")}
                  role="button"
                  tabIndex={0}
                />
                <div
                  className="gp-grid-tile gp-tile-plus"
                  style={{
                    backgroundImage: "linear-gradient(rgba(0,0,0,0.38), rgba(0,0,0,0.38)), url('/images/home/last-weekend-sunset.jpg'), linear-gradient(135deg, #ff7e5f 0%, #feb47b 100%)",
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                  }}
                  onClick={() => setCurrentScreen("search")}
                  role="button"
                  tabIndex={0}
                >
                  <span className="gp-plus-text">+18</span>
                </div>
              </div>
            </section>

            {/* Timeline: September 2024 */}
            <section className="gp-home-timeline-group">
              <div className="gp-group-header">
                <div>
                  <h3 className="gp-group-title">September 2024</h3>
                  <span className="gp-group-sub">Sonoma &amp; High Sierras • 42 photos</span>
                </div>
                <MoreHorizontal size={18} color="#5F6368" />
              </div>

              <div className="gp-four-grid-collage">
                <div
                  className="gp-grid-tile-lg"
                  style={{
                    backgroundImage: "linear-gradient(180deg, rgba(0,0,0,0) 50%, rgba(0,0,0,0.5) 100%), url('/images/home/sept-celebration.jpg'), linear-gradient(135deg, #d38312 0%, #a83279 100%)",
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                  }}
                  onClick={() => navigateToMemorySearch("celebration with flowers")}
                  role="button"
                  tabIndex={0}
                >
                  <span className="gp-split-photo-tag">Celebration</span>
                </div>
                <div
                  className="gp-grid-tile-lg"
                  style={{
                    backgroundImage: "url('/images/home/sept-dinner.jpg'), linear-gradient(135deg, #870000 0%, #190a05 100%)",
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                  }}
                  onClick={() => navigateToMemorySearch("dinner toast with friends outdoors")}
                  role="button"
                  tabIndex={0}
                />
                <div
                  className="gp-grid-tile-tall"
                  style={{
                    backgroundImage: "url('/images/home/sept-redwood.jpg'), linear-gradient(135deg, #134e5e 0%, #71b280 100%)",
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                  }}
                  onClick={() => navigateToMemorySearch("hiking in redwood forest trees")}
                  role="button"
                  tabIndex={0}
                />
                <div
                  className="gp-grid-tile-tall"
                  style={{
                    backgroundImage: "url('/images/home/sept-autumn-trail.jpg'), linear-gradient(135deg, #ba8b02 0%, #181818 100%)",
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                  }}
                  onClick={() => navigateToMemorySearch("autumn trail in the woods")}
                  role="button"
                  tabIndex={0}
                />
              </div>
            </section>
          </div>

          {/* Floating Pill Bottom Navigation Bar */}
          <div className="gp-home-floating-nav-bar">
            {/* Pill Capsule Group */}
            <div className="gp-nav-capsule">
              <button
                type="button"
                className="gp-capsule-item active"
                onClick={() => setCurrentScreen("photos")}
              >
                <span className="gp-capsule-icon">🖼️</span>
                <span className="gp-capsule-label">Photos</span>
              </button>
              <button
                type="button"
                className="gp-capsule-item"
                onClick={() => setCurrentScreen("search")}
              >
                <span className="gp-capsule-icon">📊</span>
              </button>
              <button
                type="button"
                className="gp-capsule-item"
                onClick={() => setCurrentScreen("search")}
              >
                <span className="gp-capsule-icon">✏️</span>
              </button>
              <button
                type="button"
                className="gp-capsule-item"
                onClick={() => setCurrentScreen("search")}
              >
                <span className="gp-capsule-icon">📖</span>
              </button>
            </div>

            {/* Detached Circular Search Button */}
            <button
              type="button"
              className="gp-nav-search-circle-btn"
              onClick={() => setCurrentScreen("search")}
              title="Search photos"
            >
              <Search size={20} color="#1A73E8" />
            </button>
          </div>
        </div>
      )}

      {/* =================================================================== */}
      {/* SCREEN 3: GOOGLE PHOTOS SEARCH HUB                                 */}
      {/* =================================================================== */}
      {currentScreen === "search" && (
        <div className="gp-search-screen">
          {/* Top Header - Back Button Only (Matching approved screenshot) */}
          <div className="gp-search-header-row">
            <button
              type="button"
              className="gp-header-back-btn"
              onClick={() => setCurrentScreen("photos")}
              title="Back to Photos"
            >
              <ArrowLeft size={22} color="#202124" />
            </button>
          </div>

          <div className="gp-search-scroll-body">
            {/* People & Pets Row (Preserved Real Photos + Milo Puppy) */}
            <section className="gp-people-section">
              <div className="gp-people-row">
                {[
                  { name: "Arjun", img: "/images/people/person-1.jpg", bg: "#1A73E8", letter: "A" },
                  { name: "Priya", img: "/images/people/person-2.jpg", bg: "#EA4335", letter: "P" },
                  { name: "Kabir", img: "/images/people/person-3.jpg", bg: "#FBBC05", letter: "K" },
                  { name: "Milo", img: "/images/people/pet-milo.jpg", bg: "#34A853", letter: "🐶" },
                ].map((person, idx) => (
                  <div
                    key={idx}
                    className="gp-people-circle"
                    onClick={() => navigateToMemorySearch(`photo with ${person.name}`)}
                    role="button"
                    tabIndex={0}
                    title={person.name}
                    style={{ position: "relative", overflow: "hidden", backgroundColor: person.bg }}
                  >
                    <img
                      src={person.img}
                      alt={person.name}
                      className="gp-people-avatar-img"
                      style={{ position: "relative", zIndex: 1, width: "100%", height: "100%", objectFit: "cover" }}
                      onError={(e) => {
                        e.currentTarget.style.display = "none";
                      }}
                    />
                    <span
                      className="gp-people-fallback-text"
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        width: "100%",
                        height: "100%",
                        color: "#FFFFFF",
                        fontWeight: 700,
                        fontSize: person.letter === "🐶" ? "1.25rem" : "1.1rem",
                        position: "absolute",
                        top: 0,
                        left: 0,
                        zIndex: 0,
                        userSelect: "none",
                      }}
                    >
                      {person.letter}
                    </span>
                  </div>
                ))}
                <div
                  className="gp-people-circle gp-people-more"
                  onClick={() => navigateToMemorySearch("people and family")}
                  role="button"
                  tabIndex={0}
                  title="More people & pets"
                >
                  <MoreHorizontal size={20} color="#5F6368" />
                </div>
              </div>
            </section>

            {/* Recent Searches with History Clock Icons */}
            <section className="gp-recent-searches-list">
              <div
                className="gp-recent-search-row"
                onClick={() => navigateToMemorySearch("Green pancake in japan")}
                role="button"
                tabIndex={0}
              >
                <Clock size={19} color="#5F6368" className="gp-recent-search-icon" />
                <span className="gp-recent-search-text">Green pancake in japan</span>
              </div>
              <div
                className="gp-recent-search-row"
                onClick={() => navigateToMemorySearch("5 friends at the wedding")}
                role="button"
                tabIndex={0}
              >
                <Clock size={19} color="#5F6368" className="gp-recent-search-icon" />
                <span className="gp-recent-search-text">5 friends at the wedding</span>
              </div>
            </section>

            {/* Suggested Exploration Prompts */}
            <section className="gp-suggested-prompts-list">
              {[
                "Show me my first and last photo of...",
                "What were my highlights from 2025?",
                "Who do I usually go hiking with?",
                "Which colours appear most in my...",
              ].map((promptText, pIdx) => (
                <div
                  key={pIdx}
                  className={`gp-suggested-prompt-row ${pIdx === 1 ? "gp-prompt-tinted" : ""}`}
                  onClick={() => navigateToMemorySearch(promptText)}
                  role="button"
                  tabIndex={0}
                >
                  <span>{promptText}</span>
                </div>
              ))}
            </section>

            {/* PROMINENT ROUNDED RECTANGULAR MEMORY SEARCH CARD (Matching Approved Screenshot) */}
            <section
              className="gp-iridescent-memory-card"
              onClick={() => setCurrentScreen("memory-search")}
              role="button"
              tabIndex={0}
            >
              <div className="gp-iridescent-top-row">
                <div className="gp-iridescent-icon-title">
                  <MemorySearchIcon />
                  <span className="gp-iridescent-title">Memory Search</span>
                  <span className="gp-iridescent-new-pill">NEW</span>
                </div>
                <ChevronRight size={18} color="#5F6368" />
              </div>

              <div className="gp-iridescent-desc-wrap">
                <p className="gp-iridescent-desc">
                  Search your photos the way you remember them.
                </p>
                <p className="gp-iridescent-desc">
                  Describe a person, place, feeling, occasion, or memorable detail.
                </p>
              </div>

              <div className="gp-iridescent-btn-row">
                <button
                  type="button"
                  className="gp-btn-try-it-now"
                  onClick={(e) => {
                    e.stopPropagation();
                    setCurrentScreen("memory-search");
                  }}
                >
                  <span>Try it now →</span>
                </button>
              </div>
            </section>
          </div>

          {/* Large Rounded 'Search or ask' Entry at Bottom */}
          <div className="gp-search-bottom-bar-wrap">
            <div
              className="gp-search-floating-pill"
              onClick={() => setCurrentScreen("memory-search")}
              role="button"
              tabIndex={0}
            >
              <Search size={20} color="#5F6368" />
              <span className="gp-floating-pill-placeholder">Search or ask</span>
            </div>
          </div>
        </div>
      )}

      {/* =================================================================== */}
      {/* SCREENS 4, 5, 6, 7: MEMORY SEARCH, LISTENING, RESULTS, CLARIFICATION*/}
      {/* =================================================================== */}
      {(currentScreen === "memory-search" ||
        currentScreen === "listening" ||
        currentScreen === "results" ||
        currentScreen === "clarification") && (
        <MemorySearch
          currentScreen={currentScreen}
          setCurrentScreen={setCurrentScreen}
          initialQuery={selectedQuery}
          onNavigateBackToSearch={() => setCurrentScreen("search")}
        />
      )}
    </div>
  );
}
