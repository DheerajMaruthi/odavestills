import { Link } from "react-router-dom";

export const GemMark = ({ className = "h-7 w-7" }) => (
  <svg viewBox="0 0 32 32" className={className} aria-hidden="true">
    <path d="M9 5h14l6 7-13 15L3 12z" fill="none" stroke="#a8822e" strokeWidth="1.4" strokeLinejoin="round" />
    <path d="M3 12h26M9 5l3.5 7L16 27M23 5l-3.5 7L16 27M12.5 12 16 5l3.5 7" fill="none" stroke="#c9a24b" strokeWidth="1" strokeLinejoin="round" />
  </svg>
);

export const Logo = ({ to = "/", light = false }) => (
  <Link to={to} data-testid="brand-logo" className="flex items-center gap-2.5">
    <GemMark />
    <span className={`font-display text-2xl font-semibold tracking-wide ${light ? "text-[#faf8f5]" : "text-[#1c1917]"}`}>
      Odave<span className="italic text-[#a8822e]">Stills</span>
    </span>
  </Link>
);
