"use client";

import { useRef, useState, useEffect } from "react";
import { useTheme } from "@/components/ui/ThemeProvider";

export default function PullStringSwitch() {
  const { theme, toggle } = useTheme();
  const [pulling, setPulling] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReducedMotion(mq.matches);
    const handler = (e: MediaQueryListEvent) => setReducedMotion(e.matches);
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, []);

  function handlePull() {
    if (pulling) return;
    setPulling(true);
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    const duration = reducedMotion ? 50 : 520;
    timeoutRef.current = setTimeout(() => {
      toggle();
      setPulling(false);
    }, duration);
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      handlePull();
    }
  }

  const isDark = theme === "dark";

  // Bulb fill — subtle warm glow in light mode, dimmer in dark
  const bulbFill = isDark
    ? "rgba(200,170,100,0.18)"
    : "rgba(255,210,100,0.55)";
  const bulbGlowOpacity = isDark ? 0.15 : pulling ? 0.85 : 0.6;
  const stringPull = pulling && !reducedMotion ? 14 : 0;

  return (
    <button
      onClick={handlePull}
      onKeyDown={handleKeyDown}
      aria-label={`Pull to switch to ${isDark ? "light" : "dark"} mode`}
      title="Pull to switch theme"
      style={{ cursor: "pointer" }}
      className="
        group relative flex flex-col items-center
        w-10 select-none
        focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--color-ember)]
        focus-visible:ring-offset-2 focus-visible:ring-offset-transparent
        rounded-xs
      "
    >
      {/* Fixture / ceiling mount */}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="40"
        height="120"
        viewBox="0 0 40 120"
        aria-hidden="true"
        style={{ overflow: "visible" }}
      >
        {/* Ceiling mount bracket */}
        <rect x="15" y="0" width="10" height="4" rx="1" fill="var(--color-stone)" opacity="0.6" />

        {/* Fixture neck */}
        <rect x="19" y="4" width="2" height="8" fill="var(--color-stone)" opacity="0.5" />

        {/* Pull string — animates downward on pull */}
        <g
          style={{
            transform: `translateY(${stringPull}px)`,
            transition: pulling
              ? "transform 0.18s cubic-bezier(0.34, 1.56, 0.64, 1)"
              : "transform 0.42s cubic-bezier(0.22, 0.61, 0.36, 1)",
          }}
        >
          {/* String */}
          <line
            x1="20"
            y1="12"
            x2="20"
            y2="68"
            stroke="var(--color-stone)"
            strokeWidth="1"
            strokeDasharray="none"
            opacity="0.7"
          />
          {/* Ring / handle at end of string */}
          <circle
            cx="20"
            cy="72"
            r="3.5"
            fill="none"
            stroke="var(--color-stone)"
            strokeWidth="1.2"
            opacity="0.65"
          />
          {/* Small knot dot */}
          <circle cx="20" cy="68" r="1.2" fill="var(--color-stone)" opacity="0.5" />
        </g>

        {/* Bulb body */}
        <g
          style={{
            transform: pulling && !reducedMotion ? "scale(0.96)" : "scale(1)",
            transformOrigin: "20px 26px",
            transition: "transform 0.18s ease",
          }}
        >
          {/* Outer glow — only in light mode or when lit */}
          <circle
            cx="20"
            cy="26"
            r="12"
            fill="rgba(255,195,60,0.22)"
            opacity={bulbGlowOpacity}
            style={{ transition: "opacity 0.5s ease" }}
          />

          {/* Bulb glass */}
          <path
            d="M20 12 C13 12 10 18 10 24 C10 29 13 33 16 35 L16 38 L24 38 L24 35 C27 33 30 29 30 24 C30 18 27 12 20 12Z"
            fill={bulbFill}
            stroke="var(--color-stone)"
            strokeWidth="0.8"
            opacity="0.9"
            style={{ transition: "fill 0.5s ease, opacity 0.5s ease" }}
          />

          {/* Bulb filament — two curved lines */}
          <path
            d="M17 26 Q18 24 20 25 Q22 24 23 26"
            fill="none"
            stroke={isDark ? "rgba(200,160,80,0.4)" : "rgba(180,120,40,0.7)"}
            strokeWidth="0.8"
            strokeLinecap="round"
            style={{ transition: "stroke 0.5s ease" }}
          />
          <path
            d="M17 29 Q18 27 20 28 Q22 27 23 29"
            fill="none"
            stroke={isDark ? "rgba(200,160,80,0.4)" : "rgba(180,120,40,0.7)"}
            strokeWidth="0.8"
            strokeLinecap="round"
            style={{ transition: "stroke 0.5s ease" }}
          />

          {/* Base screw threads */}
          <rect x="16" y="38" width="8" height="2" rx="0.5" fill="var(--color-stone)" opacity="0.5" />
          <rect x="16.5" y="40.5" width="7" height="1.5" rx="0.5" fill="var(--color-stone)" opacity="0.4" />
          <rect x="16.5" y="42.5" width="7" height="1.5" rx="0.5" fill="var(--color-stone)" opacity="0.3" />

          {/* Base cap */}
          <rect x="16" y="44" width="8" height="2" rx="0.5" fill="var(--color-stone)" opacity="0.45" />
        </g>
      </svg>

      {/* Tooltip label — visible on hover */}
      <span
        className="
          absolute top-full mt-1.5 left-1/2 -translate-x-1/2
          px-2 py-1 rounded-xs
          text-[10px] font-medium font-mono whitespace-nowrap
          bg-surface border border-rule text-ink
          opacity-0 group-hover:opacity-100 group-focus-visible:opacity-100
          pointer-events-none
          transition-opacity duration-200 shadow-sm
        "
      >
        {isDark ? "turn on" : "turn off"}
      </span>
    </button>
  );
}
