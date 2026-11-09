import { useState } from "react";
import { Download } from "lucide-react";
import { toast } from "sonner";
import Uploader from "@/components/studio/Uploader";
import ResultsCanvas from "@/components/studio/ResultsCanvas";
import { StudioLayout, GenerateBar } from "@/components/studio/StudioLayout";
import { Chips, Step } from "@/components/studio/Controls";
import { useGeneration } from "@/components/studio/useGeneration";
import { fileUrl, useCatalog } from "@/lib/api";

const COLOURS = [
  { id: "transparent", label: "Transparent", value: null },
  { id: "white", label: "White", value: "#ffffff" },
  { id: "ivory", label: "Ivory", value: "#f5efe4" },
  { id: "black", label: "Black", value: "#0f0e0d" },
  { id: "maroon", label: "Maroon", value: "#5a1a22" },
  { id: "emerald", label: "Emerald", value: "#0f3b2e" },
];

async function downloadComposite(url, colour) {
  const blob = await (await fetch(url)).blob();
  const bmp = await createImageBitmap(blob);
  const canvas = Object.assign(document.createElement("canvas"), { width: bmp.width, height: bmp.height });
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = colour;
  ctx.fillRect(0, 0, bmp.width, bmp.height);
  ctx.drawImage(bmp, 0, 0);
  const a = Object.assign(document.createElement("a"), { href: canvas.toDataURL("image/png"), download: "auragem-background.png" });
  a.click();
}

export default function BackgroundRemoval() {
  const { data: cat } = useCatalog();
  const gen = useGeneration();
  const [upload, setUpload] = useState(null);
  const [category, setCategory] = useState("ring");
  const [colour, setColour] = useState("transparent");
  const [custom, setCustom] = useState("#c9a24b");
  const bg = colour === "custom" ? custom : COLOURS.find((c) => c.id === colour)?.value;

  const generate = () => gen.submit.mutate({ mode: "bg_removal", upload_id: upload.id, category });

  const replaceTools = (job) => job.outputs.length > 0 && (
    <div data-testid="bg-replace-panel" className="flex flex-wrap items-center gap-3 rounded-lg border border-[#2f2a25] bg-[#1b1815] p-4">
      <span className="text-xs uppercase tracking-[0.16em] text-[#a39b8f]">Replace background</span>
      {COLOURS.map((c) => (
        <button key={c.id} data-testid={`bg-colour-${c.id}`} onClick={() => setColour(c.id)} title={c.label}
          className={`h-8 w-8 rounded-full border-2 ${colour === c.id ? "border-[#c9a24b]" : "border-[#3a342e]"} ${c.value ? "" : "checkerboard"}`}
          style={c.value ? { background: c.value } : undefined} />
      ))}
      <label className={`flex h-8 items-center gap-2 rounded-full border-2 px-2 text-xs text-[#e8e2d6] ${colour === "custom" ? "border-[#c9a24b]" : "border-[#3a342e]"}`}>
        <input data-testid="bg-colour-custom" type="color" value={custom} onChange={(e) => { setCustom(e.target.value); setColour("custom"); }} className="h-5 w-5 cursor-pointer bg-transparent" />
        Custom
      </label>
      {bg && (
        <button data-testid="bg-download-composite" onClick={() => downloadComposite(fileUrl(job.outputs[0].url), bg).catch(() => toast.error("Download failed"))}
          className="ml-auto inline-flex items-center gap-1.5 rounded-md bg-[#c9a24b] px-3 py-2 text-xs font-medium text-[#1c1917] hover:bg-[#d8b45f]">
          <Download className="h-3.5 w-3.5" /> Download with background
        </button>
      )}
    </div>
  );

  const controls = (
    <div data-testid="bg-controls">
      <div className="px-6 pb-2 pt-8">
        <p className="eyebrow">Cut-out tool</p>
        <h1 className="mt-2 font-display text-4xl text-[#1c1917]">Background removal</h1>
      </div>
      <Step n={1} title="Upload photo"><Uploader upload={upload} onChange={setUpload} /></Step>
      <Step n={2} title="Jewellery type" hint="Helps the AI detect exactly which object to keep.">
        <Chips options={cat?.categories} value={category} onChange={setCategory} testid="category" />
      </Step>
      <Step n={3} title="Output">
        <p className="text-sm text-[#57534e]">A transparent PNG, cropped to the jewellery. Preview it on any colour and download the transparent or filled version.</p>
      </Step>
      <GenerateBar cost={cat?.credit_cost?.bg_removal || 1} disabled={!upload} onClick={generate} job={gen.job} pending={gen.submit.isPending} label="Remove background" />
    </div>
  );

  return (
    <StudioLayout controls={controls} canvas={
      <ResultsCanvas job={gen.job} gen={gen} background={bg || undefined} renderExtra={replaceTools}
        emptyTitle="Clean cut-outs, ready for anywhere." emptyText="Remove clutter, hands and stands from your photo and get a transparent PNG for your website, marketplace listings or catalogues." />
    } />
  );
}
