import { useState } from "react";
import { Columns2, Download, FolderPlus, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import QualityBadge from "@/components/studio/QualityBadge";
import CompareSlider from "@/components/studio/CompareSlider";
import SaveToProjectDialog from "@/components/studio/SaveToProjectDialog";
import { errMsg, fileUrl, useApi } from "@/lib/api";

const IconBtn = ({ onClick, label, icon: Icon, testid, danger, href }) => {
  const cls = `inline-flex h-8 w-8 items-center justify-center rounded-md border border-[#e4ded4] bg-white transition-colors ${
    danger ? "hover:border-[#f1caca] hover:text-[#b91c1c]" : "hover:border-[#c9a24b]"}`;
  return href ? (
    <a href={href} data-testid={testid} aria-label={label} title={label} className={cls}><Icon className="h-3.5 w-3.5" /></a>
  ) : (
    <button onClick={onClick} data-testid={testid} aria-label={label} title={label} className={cls}><Icon className="h-3.5 w-3.5" /></button>
  );
};

export default function ImageCard({ image, onChanged, background, large = false }) {
  const api = useApi();
  const [compare, setCompare] = useState(false);
  const [save, setSave] = useState(false);
  const png = image.content_type === "image/png";

  const remove = async () => {
    if (!window.confirm("Delete this image? This cannot be undone.")) return;
    try {
      await api.delete(`/images/${image.id}`);
      toast.success("Image deleted");
      onChanged?.();
    } catch (e) {
      toast.error(errMsg(e));
    }
  };

  return (
    <figure data-testid={`image-card-${image.id}`} className="group overflow-hidden rounded-lg border border-[#e4ded4] bg-white">
      <button onClick={() => setCompare(true)} className={`relative block w-full ${png ? "checkerboard" : "bg-[#f3efe8]"}`}
        style={background ? { background } : undefined} data-testid={`image-open-${image.id}`}>
        <img src={fileUrl(image.url)} alt={`${image.category} ${image.mode}`} loading="lazy"
          className={`w-full object-contain transition-transform duration-500 group-hover:scale-[1.02] ${large ? "aspect-square" : "aspect-[4/5]"}`} />
        {image.is_mock && <span className="absolute left-2 top-2 rounded bg-[#1c1917] px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-[#e2c47e]">Mock</span>}
        {image.quality?.pixel_exact && <span data-testid={`pixel-exact-tag-${image.id}`} className="absolute right-2 top-2 rounded bg-[#1c1917]/85 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-[#e2c47e]">Original pixels</span>}
      </button>
      <figcaption className="flex flex-wrap items-center justify-between gap-2 p-3">
        <QualityBadge quality={image.quality} testid={`quality-badge-${image.id}`} />
        <div className="flex gap-1.5">
          <IconBtn onClick={() => setCompare(true)} label="Compare with original" icon={Columns2} testid={`image-compare-${image.id}`} />
          <IconBtn href={fileUrl(image.download_url)} label="Download" icon={Download} testid={`image-download-${image.id}`} />
          <IconBtn onClick={() => setSave(true)} label="Save to project" icon={FolderPlus} testid={`image-save-${image.id}`} />
          <IconBtn onClick={remove} label="Delete" icon={Trash2} testid={`image-delete-${image.id}`} danger />
        </div>
      </figcaption>
      <Dialog open={compare} onOpenChange={setCompare}>
        <DialogContent className="max-w-4xl p-0" data-testid="compare-dialog">
          <DialogHeader className="px-6 pt-6"><DialogTitle className="font-display text-2xl font-medium">Original vs generated</DialogTitle></DialogHeader>
          <CompareSlider before={fileUrl(image.original_url)} after={fileUrl(image.url)} transparent={png} className="max-h-[75vh] w-full" style={{ aspectRatio: `${image.width} / ${image.height}` }} />
        </DialogContent>
      </Dialog>
      <SaveToProjectDialog image={image} open={save} onOpenChange={setSave} onSaved={onChanged} />
    </figure>
  );
}
