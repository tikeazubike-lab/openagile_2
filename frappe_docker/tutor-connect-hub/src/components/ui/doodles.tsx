import { cn } from "@/lib/utils";

/* ---------------------------------- Waves --------------------------------- */

interface WaveProps {
  fill?: string;
  flip?: boolean;
  className?: string;
}

/** Smooth sine wave divider (Kidza-style) */
export function Wave({ fill = "#FFFFFF", flip = false, className }: WaveProps) {
  return (
    <svg
      viewBox="0 0 1440 90"
      preserveAspectRatio="none"
      aria-hidden="true"
      className={cn("block h-[50px] w-full sm:h-[70px]", flip && "rotate-180", className)}
    >
      <path
        d="M0,50 C120,90 240,90 360,60 C480,30 600,10 720,30 C840,50 960,85 1080,75 C1200,65 1320,30 1440,45 L1440,90 L0,90 Z"
        fill={fill}
      />
    </svg>
  );
}

/** Scalloped cloud edge (signature Kidza wavy border) */
export function ScallopEdge({ fill = "#FFFFFF", flip = false, className }: WaveProps) {
  const bumps = Array.from({ length: 16 }, (_, i) => {
    const x = i * 90;
    return `Q${x + 45},0 ${x + 90},35`;
  }).join(" ");
  return (
    <svg
      viewBox="0 0 1440 60"
      preserveAspectRatio="none"
      aria-hidden="true"
      className={cn("block h-[30px] w-full sm:h-[45px]", flip && "rotate-180", className)}
    >
      <path d={`M0,60 L0,35 ${bumps} L1440,60 Z`} fill={fill} />
    </svg>
  );
}

/** Grass strip for footer top edge */
export function GrassEdge({ className }: { className?: string }) {
  const blades = Array.from({ length: 24 }, (_, i) => {
    const x = i * 60;
    return `M${x},40 Q${x + 15},${8 + (i % 3) * 4} ${x + 30},40`;
  }).join(" ");
  return (
    <svg
      viewBox="0 0 1440 40"
      preserveAspectRatio="none"
      aria-hidden="true"
      className={cn("block h-[24px] w-full sm:h-[36px]", className)}
    >
      <path d={`M0,40 ${blades} L1440,40 Z`} fill="#4ADE80" />
    </svg>
  );
}

/* --------------------------------- Doodles -------------------------------- */

interface DoodleProps {
  className?: string;
}

/** Hand-drawn lightbulb */
export function LightbulbDoodle({ className }: DoodleProps) {
  return (
    <svg viewBox="0 0 64 64" fill="none" aria-hidden="true" className={className}>
      <path
        d="M32 8c-9 0-16 7-16 15.5 0 5.5 3 9.5 6 12.5 2.5 2.5 4 5.5 4.5 9h11c.5-3.5 2-6.5 4.5-9 3-3 6-7 6-12.5C48 15 41 8 32 8Z"
        fill="#FFD93D"
        stroke="#1F2937"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
      <path d="M27 50h10M28.5 55h7" stroke="#1F2937" strokeWidth="2.5" strokeLinecap="round" />
      <path d="M32 2v4M12 12l3 3M52 12l-3 3M6 26h5M53 26h5" stroke="#FF8C42" strokeWidth="2.5" strokeLinecap="round" />
    </svg>
  );
}

/** Hand-drawn crown */
export function CrownDoodle({ className }: DoodleProps) {
  return (
    <svg viewBox="0 0 64 48" fill="none" aria-hidden="true" className={className}>
      <path
        d="M6 38 10 14l12 10L32 6l10 18 12-10 4 24H6Z"
        fill="#FFD93D"
        stroke="#1F2937"
        strokeWidth="2.5"
        strokeLinejoin="round"
      />
      <circle cx="32" cy="30" r="3" fill="#6C5CE7" stroke="#1F2937" strokeWidth="2" />
      <circle cx="10" cy="12" r="3" fill="#FF8C42" stroke="#1F2937" strokeWidth="2" />
      <circle cx="54" cy="12" r="3" fill="#FF8C42" stroke="#1F2937" strokeWidth="2" />
      <circle cx="32" cy="4" r="3" fill="#6C5CE7" stroke="#1F2937" strokeWidth="2" />
    </svg>
  );
}

/** Hand-drawn flower */
export function FlowerDoodle({ className }: DoodleProps) {
  return (
    <svg viewBox="0 0 64 64" fill="none" aria-hidden="true" className={className}>
      {[0, 60, 120, 180, 240, 300].map((deg) => (
        <ellipse
          key={deg}
          cx="32"
          cy="16"
          rx="7"
          ry="11"
          fill="#FFB7C5"
          stroke="#1F2937"
          strokeWidth="2"
          transform={`rotate(${deg} 32 32)`}
        />
      ))}
      <circle cx="32" cy="32" r="8" fill="#FFD93D" stroke="#1F2937" strokeWidth="2.5" />
      <path d="M32 42v16M32 50c-4-2-8-1-10 2M32 54c4-2 8-1 10 2" stroke="#22C55E" strokeWidth="2.5" strokeLinecap="round" />
    </svg>
  );
}

/** Lightning bolt doodle */
export function LightningDoodle({ className }: DoodleProps) {
  return (
    <svg viewBox="0 0 48 64" fill="none" aria-hidden="true" className={className}>
      <path
        d="M28 4 10 36h12l-4 24 20-34H26l2-22Z"
        fill="#FFD93D"
        stroke="#1F2937"
        strokeWidth="2.5"
        strokeLinejoin="round"
      />
    </svg>
  );
}

/** Heart doodle */
export function HeartDoodle({ className }: DoodleProps) {
  return (
    <svg viewBox="0 0 64 56" fill="none" aria-hidden="true" className={className}>
      <path
        d="M32 52C18 42 4 30 4 18 4 9 11 4 18 4c6 0 11 4 14 8 3-4 8-8 14-8 7 0 14 5 14 14 0 12-14 24-28 34Z"
        fill="#FFB7C5"
        stroke="#1F2937"
        strokeWidth="2.5"
        strokeLinejoin="round"
      />
    </svg>
  );
}

/** Sparkle / plus doodle */
export function SparkleDoodle({ className }: DoodleProps) {
  return (
    <svg viewBox="0 0 48 48" fill="none" aria-hidden="true" className={className}>
      <path
        d="M24 4v40M4 24h40M11 11l26 26M37 11 11 37"
        stroke="#FF8C42"
        strokeWidth="3"
        strokeLinecap="round"
      />
    </svg>
  );
}

/** Paper-plane doodle */
export function PlaneDoodle({ className }: DoodleProps) {
  return (
    <svg viewBox="0 0 64 64" fill="none" aria-hidden="true" className={className}>
      <path
        d="M58 8 28 36M58 8 38 58l-10-22M58 8 6 28l22 8"
        fill="#A0E7E5"
        stroke="#1F2937"
        strokeWidth="2.5"
        strokeLinejoin="round"
      />
    </svg>
  );
}

/** Sun doodle */
export function SunDoodle({ className }: DoodleProps) {
  return (
    <svg viewBox="0 0 64 64" fill="none" aria-hidden="true" className={className}>
      <circle cx="32" cy="32" r="14" fill="#FFD93D" stroke="#1F2937" strokeWidth="2.5" />
      {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => (
        <line
          key={deg}
          x1="32"
          y1="8"
          x2="32"
          y2="16"
          stroke="#FF8C42"
          strokeWidth="3"
          strokeLinecap="round"
          transform={`rotate(${deg} 32 32)`}
        />
      ))}
    </svg>
  );
}
