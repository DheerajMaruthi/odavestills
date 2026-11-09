import { Loader2, Sparkles } from "lucide-react";
import { isRunning } from "@/components/studio/useGeneration";
import { useMe } from "@/lib/api";

export const StudioLayout = ({ controls, canvas }) => (
  <div className="grid lg:grid-cols-[420px_1fr]">
    <div className="border-r border-[#ebe5da] bg-[#fbf9f6] lg:h-[calc(100vh)] lg:overflow-y-auto">{controls}</div>
    <div className="lg:h-[calc(100vh)] lg:overflow-y-auto">{canvas}</div>
  </div>
);

export function GenerateBar({ cost, disabled, onClick, job, pending, label = "Generate" }) {
  const { data: me } = useMe();
  const busy = pending || isRunning(job);
  const short = me && me.credits < cost;
  return (
    <div className="sticky bottom-0 space-y-2 border-t border-[#ebe5da] bg-[#fbf9f6]/95 px-6 py-4 backdrop-blur">
      <button data-testid="generate-btn" onClick={onClick} disabled={disabled || busy || short}
        className="flex w-full items-center justify-center gap-2 rounded-md bg-[#1c1917] px-6 py-3.5 text-sm font-medium text-[#faf8f5] transition-colors hover:bg-[#2c2724] disabled:cursor-not-allowed disabled:opacity-50">
        {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4 text-[#e2c47e]" />}
        {busy ? "Generating…" : `${label} · ${cost} credit${cost > 1 ? "s" : ""}`}
      </button>
      <p className="text-center text-[11px] text-[#78716c]" data-testid="generate-credit-note">
        {short ? "Not enough credits — top up in Billing." : `Balance ${me?.credits ?? "–"} · failed images are refunded automatically`}
      </p>
    </div>
  );
}
