import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Textarea } from "@/components/ui/textarea";
import Uploader from "@/components/studio/Uploader";
import ResultsCanvas from "@/components/studio/ResultsCanvas";
import ProjectPicker from "@/components/studio/ProjectPicker";
import { StudioLayout, GenerateBar } from "@/components/studio/StudioLayout";
import { Chips, Counter, Field, Step, Swatches } from "@/components/studio/Controls";
import { useGeneration } from "@/components/studio/useGeneration";
import { useCatalog } from "@/lib/api";

const DEFAULTS = { accuracy: "exact", lighting: "soft_diffused", angle: "three_quarter", background: "auto", aspect_ratio: "1:1", dimensions: "1536", instructions: "" };

export default function Studio() {
  const { data: cat } = useCatalog();
  const [params] = useSearchParams();
  const gen = useGeneration();
  const [upload, setUpload] = useState(null);
  const [category, setCategory] = useState("necklace");
  const [style, setStyle] = useState("luxury_black");
  const [s, setS] = useState(DEFAULTS);
  const [count, setCount] = useState(1);
  const [projectId, setProjectId] = useState(params.get("project"));
  const set = (k) => (v) => setS((p) => ({ ...p, [k]: v }));
  const cost = (cat?.credit_cost?.product || 1) * count;

  const generate = () =>
    gen.submit.mutate({ mode: "product", upload_id: upload.id, category, style, settings: s, output_count: count, project_id: projectId });

  const controls = (
    <div data-testid="studio-controls">
      <div className="px-6 pb-2 pt-8">
        <p className="eyebrow">Product studio</p>
        <h1 className="mt-2 font-display text-4xl text-[#1c1917]">Studio photography</h1>
      </div>
      <Step n={1} title="Upload photo"><Uploader upload={upload} onChange={setUpload} projectId={projectId} /></Step>
      <Step n={2} title="Jewellery type"><Chips options={cat?.categories} value={category} onChange={setCategory} testid="category" /></Step>
      <Step n={3} title="Design accuracy">
        <div className="grid gap-2.5" data-testid="accuracy">
          {cat?.accuracy?.map((a) => (
            <button key={a.id} type="button" data-testid={`accuracy-${a.id}`} onClick={() => set("accuracy")(a.id)}
              className={`rounded-md border p-3.5 text-left transition-colors ${s.accuracy === a.id ? "border-[#c9a24b] bg-[#f6efdc]/70 ring-1 ring-[#c9a24b]/50" : "border-[#e4ded4] bg-white hover:border-[#c9a24b]"}`}>
              <p className="text-sm font-medium text-[#1c1917]">{a.label}{a.id === "exact" && <span className="ml-2 rounded-full bg-[#1c1917] px-2 py-0.5 text-[10px] uppercase tracking-wider text-[#e2c47e]">100% design</span>}</p>
              <p className="mt-1 text-xs leading-relaxed text-[#78716c]">{a.description}</p>
            </button>
          ))}
        </div>
      </Step>
      <Step n={4} title="Photography style"><Swatches options={cat?.styles} value={style} onChange={setStyle} testid="style" /></Step>
      <Step n={5} title="Customise">
        <div className="grid grid-cols-2 gap-3">
          <Field label="Background" value={s.background} onChange={set("background")} options={cat?.backgrounds} testid="setting-background" />
          <Field label="Lighting" value={s.lighting} onChange={set("lighting")} options={cat?.lighting} testid="setting-lighting" />
          <Field label="Camera angle" value={s.angle} onChange={set("angle")} options={cat?.angles} testid="setting-angle" />
          <Field label="Aspect ratio" value={s.aspect_ratio} onChange={set("aspect_ratio")} options={cat?.aspect_ratios} testid="setting-aspect" />
          <div className="col-span-2"><Field label="Image size" value={s.dimensions} onChange={set("dimensions")} options={cat?.dimensions} testid="setting-dimensions" /></div>
        </div>
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-[#57534e]">Number of images</label>
          <Counter value={count} onChange={setCount} max={cat?.max_outputs || 4} testid="output-count" />
        </div>
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-[#57534e]">Additional instructions</label>
          <Textarea data-testid="setting-instructions" rows={3} maxLength={500} value={s.instructions} onChange={(e) => set("instructions")(e.target.value)}
            placeholder="e.g. add a few rose petals, keep the shadow soft" className="bg-white text-sm" />
        </div>
        <ProjectPicker value={projectId} onChange={setProjectId} />
      </Step>
      <GenerateBar cost={cost} disabled={!upload} onClick={generate} job={gen.job} pending={gen.submit.isPending} />
    </div>
  );

  return (
    <StudioLayout controls={controls} canvas={
      <ResultsCanvas job={gen.job} gen={gen} emptyTitle="Your lightbox awaits."
        emptyText="Upload a phone photo of a single piece, choose a style and generate. Every result is checked against your original for design fidelity." />
    } />
  );
}
