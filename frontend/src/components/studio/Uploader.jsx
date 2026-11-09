import { useRef, useState } from "react";
import { ImagePlus, Loader2, RefreshCw, X } from "lucide-react";
import { toast } from "sonner";
import { errMsg, formatBytes, useApi } from "@/lib/api";

const TYPES = ["image/jpeg", "image/png", "image/webp"];
const MAX = 15 * 1024 * 1024;

const readDims = (src) =>
  new Promise((res, rej) => {
    const img = new Image();
    img.onload = () => res({ width: img.naturalWidth, height: img.naturalHeight });
    img.onerror = rej;
    img.src = src;
  });

export default function Uploader({ upload, onChange, projectId }) {
  const api = useApi();
  const input = useRef(null);
  const [drag, setDrag] = useState(false);
  const [busy, setBusy] = useState(false);
  const [preview, setPreview] = useState(null);

  const handle = async (file) => {
    if (!file) return;
    if (!TYPES.includes(file.type)) return toast.error("Please upload a JPEG, PNG or WebP image");
    if (file.size > MAX) return toast.error("Image must be 15 MB or smaller");
    const src = URL.createObjectURL(file);
    try {
      const { width, height } = await readDims(src);
      if (Math.min(width, height) < 256) return toast.error(`Image is too small (${width}×${height}). Use at least 256px.`);
    } catch {
      return toast.error("This file could not be read as an image");
    }
    setPreview(src);
    setBusy(true);
    const form = new FormData();
    form.append("file", file);
    if (projectId) form.append("project_id", projectId);
    try {
      const { data } = await api.post("/uploads", form);
      onChange(data);
    } catch (e) {
      toast.error(errMsg(e, "Upload failed"));
      setPreview(null);
      onChange(null);
    } finally {
      setBusy(false);
    }
  };

  const clear = () => { setPreview(null); onChange(null); };

  if (preview || upload) {
    return (
      <div data-testid="upload-preview" className="overflow-hidden rounded-lg border border-[#e4ded4] bg-white">
        <div className="relative flex aspect-[4/3] items-center justify-center bg-[#f3efe8]">
          <img src={preview || upload.url} alt="Uploaded jewellery" className="h-full w-full object-contain" />
          {busy && <div className="absolute inset-0 flex items-center justify-center bg-white/60"><Loader2 className="h-6 w-6 animate-spin text-[#a8822e]" /></div>}
        </div>
        <div className="flex items-center justify-between gap-2 px-3 py-2.5 text-xs text-[#57534e]">
          <span className="truncate" data-testid="upload-meta">
            {upload ? `${upload.width}×${upload.height}px · ${formatBytes(upload.size_bytes)}` : "Uploading…"}
          </span>
          <div className="flex gap-1">
            <button data-testid="upload-replace-btn" onClick={() => input.current?.click()} className="rounded p-1.5 hover:bg-[#f3efe8]" aria-label="Replace image"><RefreshCw className="h-3.5 w-3.5" /></button>
            <button data-testid="upload-remove-btn" onClick={clear} className="rounded p-1.5 hover:bg-[#f3efe8]" aria-label="Remove image"><X className="h-3.5 w-3.5" /></button>
          </div>
        </div>
        <input ref={input} type="file" accept={TYPES.join(",")} className="hidden" onChange={(e) => handle(e.target.files?.[0])} />
      </div>
    );
  }

  return (
    <label data-testid="upload-dropzone"
      onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
      onDragLeave={() => setDrag(false)}
      onDrop={(e) => { e.preventDefault(); setDrag(false); handle(e.dataTransfer.files?.[0]); }}
      className={`flex cursor-pointer flex-col items-start gap-3 rounded-lg border border-dashed p-6 transition-colors ${
        drag ? "border-[#c9a24b] bg-[#f6efdc]" : "border-[#d6ccba] bg-white hover:bg-[#fbf8f2]"}`}>
      <ImagePlus className="h-6 w-6 text-[#a8822e]" strokeWidth={1.5} />
      <div>
        <p className="text-sm font-medium text-[#1c1917]">Drop a jewellery photo, or browse</p>
        <p className="mt-1 text-xs text-[#78716c]">JPEG, PNG or WebP · up to 15 MB · a plain, well-lit phone photo works best</p>
      </div>
      <input ref={input} data-testid="upload-input" type="file" accept={TYPES.join(",")} className="hidden" onChange={(e) => handle(e.target.files?.[0])} />
    </label>
  );
}
