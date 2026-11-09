import { useState } from "react";

export default function CompareSlider({ before, after, testid = "compare-slider", transparent = false, className = "", fit = "object-contain", style }) {
  const [pos, setPos] = useState(50);
  return (
    <div data-testid={testid} style={style} className={`relative select-none overflow-hidden ${transparent ? "checkerboard" : "bg-[#141210]"} ${className}`}>
      <img src={after} alt="Generated" className={`block h-full w-full ${fit}`} draggable={false} />
      <div className="absolute inset-0" style={{ clipPath: `inset(0 ${100 - pos}% 0 0)` }}>
        <img src={before} alt="Original" className={`h-full w-full bg-[#141210] ${fit}`} draggable={false} />
      </div>
      <div className="pointer-events-none absolute inset-y-0" style={{ left: `${pos}%` }}>
        <div className="h-full w-px bg-[#e2c47e]" />
        <div className="absolute top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full border border-[#e2c47e] bg-[#141210]/80 px-2 py-1 text-[10px] tracking-widest text-[#e2c47e]">⟷</div>
      </div>
      <span className="absolute left-3 top-3 rounded bg-black/55 px-2 py-0.5 text-[10px] uppercase tracking-widest text-white">Original</span>
      <span className="absolute right-3 top-3 rounded bg-[#c9a24b] px-2 py-0.5 text-[10px] uppercase tracking-widest text-[#1c1917]">AuraGem</span>
      <input type="range" min="0" max="100" value={pos} onChange={(e) => setPos(+e.target.value)} aria-label="Compare original and generated"
        data-testid={`${testid}-range`} className="absolute inset-0 h-full w-full cursor-ew-resize opacity-0" />
    </div>
  );
}
