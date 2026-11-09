import { ShieldCheck, ShieldAlert, ShieldQuestion } from "lucide-react";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";

const TONE = {
  high_fidelity: { cls: "bg-[#ecf5ee] text-[#166534] border-[#cfe5d5]", Icon: ShieldCheck },
  review: { cls: "bg-[#fbf3e2] text-[#92400e] border-[#f0dfb8]", Icon: ShieldAlert },
  altered: { cls: "bg-[#fbeaea] text-[#991b1b] border-[#f1caca]", Icon: ShieldAlert },
  unverified: { cls: "bg-[#f3f1ee] text-[#57534e] border-[#e4ded4]", Icon: ShieldQuestion },
};

const Metric = ({ label, value }) =>
  value == null ? null : (
    <div className="flex justify-between text-xs"><span className="text-[#78716c]">{label}</span><span className="font-medium">{value}</span></div>
  );

export default function QualityBadge({ quality, testid }) {
  if (!quality) return null;
  const { cls, Icon } = TONE[quality.verdict] || TONE.unverified;
  const ins = quality.inspector || {};
  return (
    <Popover>
      <PopoverTrigger asChild>
        <button data-testid={testid} className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-medium ${cls}`}>
          <Icon className="h-3.5 w-3.5" />
          {quality.score != null ? `${quality.score}/10` : "—"} · {quality.label}
        </button>
      </PopoverTrigger>
      <PopoverContent className="w-72 space-y-3" data-testid={`${testid}-details`}>
        <p className="eyebrow">Design fidelity check</p>
        <div className="space-y-1.5">
          <Metric label="Shape" value={ins.shape} />
          <Metric label="Stones" value={ins.stones} />
          <Metric label="Metal colour" value={ins.metal_colour} />
          <Metric label="Fine details" value={ins.details} />
          <Metric label="Colour match (pixel)" value={quality.local?.colour_similarity} />
          <Metric label="Proportions (pixel)" value={quality.local?.shape_ratio_similarity} />
        </div>
        {quality.issues?.length > 0 && (
          <ul className="list-disc space-y-1 pl-4 text-xs text-[#44403c]">{quality.issues.map((i) => <li key={i}>{i}</li>)}</ul>
        )}
        {!quality.inspector_available && <p className="text-xs text-[#92400e]">{quality.pixel_exact ? "Jewellery uses your original pixels. The AI inspector did not run, so check the cut-out edges." : "AI inspector unavailable. The score uses pixel metrics only."}</p>}
        <p className="text-[11px] leading-relaxed text-[#78716c]">{quality.note}</p>
      </PopoverContent>
    </Popover>
  );
}
