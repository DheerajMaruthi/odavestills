import { useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import Uploader from "@/components/studio/Uploader";
import ResultsCanvas from "@/components/studio/ResultsCanvas";
import ProjectPicker from "@/components/studio/ProjectPicker";
import { StudioLayout, GenerateBar } from "@/components/studio/StudioLayout";
import { Chips, Counter, Field, Step } from "@/components/studio/Controls";
import { useGeneration } from "@/components/studio/useGeneration";
import { useCatalog } from "@/lib/api";

const PRESET_IMAGES = {
  traditional_bridal: "https://images.unsplash.com/photo-1600685890506-593fdf55949b?auto=format&fit=crop&w=400&q=70",
  south_indian: "https://images.unsplash.com/photo-1688382654723-a7366006519b?auto=format&fit=crop&w=400&q=70",
  north_indian_bridal: "https://images.unsplash.com/photo-1778148046574-c1509f5a40d4?auto=format&fit=crop&w=400&q=70",
  modern_fashion: "https://images.unsplash.com/photo-1619002117199-47c7f0427d21?auto=format&fit=crop&w=400&q=70",
  festive: "https://images.unsplash.com/photo-1710655180941-056bf55fed7f?auto=format&fit=crop&w=400&q=70",
  luxury_editorial: "https://images.unsplash.com/photo-1768845431893-8e28ed7bf79e?auto=format&fit=crop&w=400&q=70",
};

const DEFAULTS = { preset: "traditional_bridal", gender: "female", appearance: "wheatish", pose: "front_portrait", clothing: "lehenga", background: "palace", aspect_ratio: "4:5", dimensions: "1536", instructions: "" };

export default function ModelStudio() {
  const { data: cat } = useCatalog();
  const gen = useGeneration();
  const [upload, setUpload] = useState(null);
  const [category, setCategory] = useState("necklace");
  const [style, setStyle] = useState("none");
  const [s, setS] = useState(DEFAULTS);
  const [count, setCount] = useState(1);
  const [projectId, setProjectId] = useState(null);
  const set = (k) => (v) => setS((p) => ({ ...p, [k]: v }));
  const cost = (cat?.credit_cost?.model || 1) * count;

  const generate = () => gen.submit.mutate({
    mode: "model", upload_id: upload.id, category, style: style === "none" ? null : style, settings: s, output_count: count, project_id: projectId,
  });

  const controls = (
    <div data-testid="model-controls">
      <div className="px-6 pb-2 pt-8">
        <p className="eyebrow">On-model photography</p>
        <h1 className="mt-2 font-display text-4xl text-[#1c1917]">Model photography</h1>
      </div>
      <Step n={1} title="Upload jewellery"><Uploader upload={upload} onChange={setUpload} /></Step>
      <Step n={2} title="Jewellery type"><Chips options={cat?.categories} value={category} onChange={setCategory} testid="category" /></Step>
      <Step n={3} title="Look & preset">
        <div className="grid grid-cols-2 gap-2.5" data-testid="model-preset">
          {cat?.model_presets.map((p) => (
            <button key={p.id} data-testid={`model-preset-${p.id}`} onClick={() => setS((prev) => ({ ...prev, preset: p.id, ...(p.defaults || {}) }))}
              className={`relative h-20 overflow-hidden rounded-md border text-left transition-shadow ${s.preset === p.id ? "border-[#c9a24b] ring-2 ring-[#c9a24b]/40" : "border-[#e4ded4] hover:shadow-md"}`}>
              {PRESET_IMAGES[p.id] ? <img src={PRESET_IMAGES[p.id]} alt="" className="absolute inset-0 h-full w-full object-cover" /> : <div className="absolute inset-0 bg-[#2a2522]" />}
              <div className="absolute inset-0 bg-gradient-to-t from-black/75 to-transparent" />
              <span className="absolute bottom-2 left-2 right-2 text-xs font-medium leading-tight text-white">{p.label}</span>
            </button>
          ))}
        </div>
      </Step>
      <Step n={4} title="Model & scene">
        <div className="grid grid-cols-2 gap-3">
          <Field label="Gender" value={s.gender} onChange={set("gender")} options={cat?.genders} testid="model-gender" />
          <Field label="Appearance" value={s.appearance} onChange={set("appearance")} options={cat?.appearances} testid="model-appearance" />
          <Field label="Pose" value={s.pose} onChange={set("pose")} options={cat?.poses} testid="model-pose" />
          <Field label="Clothing" value={s.clothing} onChange={set("clothing")} options={cat?.clothing} testid="model-clothing" />
          <Field label="Background" value={s.background} onChange={set("background")} options={cat?.model_backgrounds} testid="model-background" />
          <Field label="Photo style" value={style} onChange={setStyle} options={[{ id: "none", label: "Preset default" }, ...(cat?.styles || [])]} testid="model-style" />
          <Field label="Aspect ratio" value={s.aspect_ratio} onChange={set("aspect_ratio")} options={cat?.aspect_ratios} testid="model-aspect" />
          <Field label="Image size" value={s.dimensions} onChange={set("dimensions")} options={cat?.dimensions} testid="model-dimensions" />
        </div>
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-[#57534e]">Number of images</label>
          <Counter value={count} onChange={setCount} max={cat?.max_outputs || 4} testid="output-count" />
        </div>
        <Textarea data-testid="model-instructions" rows={2} maxLength={500} value={s.instructions} onChange={(e) => set("instructions")(e.target.value)}
          placeholder="Additional instructions (optional)" className="bg-white text-sm" />
        <ProjectPicker value={projectId} onChange={setProjectId} />
        <p className="rounded-md bg-[#f6efdc] p-3 text-[11px] leading-relaxed text-[#6b5320]">
          AI models can subtly change scale or hidden details when placing jewellery on a person. Each result gets an automated fidelity score — always review before publishing.
        </p>
      </Step>
      <GenerateBar cost={cost} disabled={!upload} onClick={generate} job={gen.job} pending={gen.submit.isPending} label="Generate model shoot" />
    </div>
  );

  return (
    <StudioLayout controls={controls} canvas={
      <ResultsCanvas job={gen.job} gen={gen} emptyTitle="Cast your campaign."
        emptyText="Place your real jewellery on an AI model — bridal, South Indian, festive or editorial — without booking a shoot." />
    } />
  );
}
