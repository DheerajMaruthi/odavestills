import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Download, ImageIcon } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import ImageCard from "@/components/studio/ImageCard";
import { Field } from "@/components/studio/Controls";
import { PageHeader, EmptyState } from "@/components/layout/PageHeader";
import { StatusPill } from "@/pages/Dashboard";
import { fileUrl, formatDate, labelOf, useApi, useCatalog } from "@/lib/api";

const MODES = [{ id: "all", label: "All tools" }, { id: "product", label: "Product studio" }, { id: "model", label: "Model photography" }, { id: "bg_removal", label: "Background removal" }];

function JobsTable() {
  const api = useApi();
  const { data: cat } = useCatalog();
  const { data: jobs, isLoading } = useQuery({ queryKey: ["jobs"], queryFn: () => api.get("/jobs").then((r) => r.data) });
  if (isLoading) return <Skeleton className="h-48" />;
  if (!jobs?.length) return <EmptyState testid="jobs-empty" title="No generation history yet" />;
  return (
    <div className="overflow-x-auto rounded-lg border border-[#ebe5da] bg-white" data-testid="jobs-table">
      <table className="w-full text-sm">
        <thead className="border-b border-[#efe9df] text-left text-xs uppercase tracking-[0.12em] text-[#78716c]">
          <tr><th className="px-5 py-3">Original</th><th className="px-5 py-3">Tool</th><th className="px-5 py-3">Type / style</th><th className="px-5 py-3">Images</th><th className="px-5 py-3">Credits</th><th className="px-5 py-3">Status</th><th className="px-5 py-3">Date</th><th /></tr>
        </thead>
        <tbody className="divide-y divide-[#efe9df]">
          {jobs.map((j) => (
            <tr key={j.id} data-testid={`job-row-${j.id}`}>
              <td className="px-5 py-3"><img src={fileUrl(j.original_url)} alt="" className="h-12 w-12 rounded object-cover" /></td>
              <td className="px-5 py-3">{labelOf(MODES, j.mode)}</td>
              <td className="px-5 py-3 text-[#57534e]">{labelOf(cat?.categories, j.category)}{j.style && ` · ${labelOf(cat?.styles, j.style)}`}</td>
              <td className="px-5 py-3">{j.outputs.length}/{j.output_count}</td>
              <td className="px-5 py-3">{j.credits_charged ?? "…"}</td>
              <td className="px-5 py-3"><StatusPill status={j.status} testid={`job-status-${j.id}`} /></td>
              <td className="px-5 py-3 text-xs text-[#78716c]">{formatDate(j.created_at)}</td>
              <td className="px-5 py-3">{j.zip_url && <a href={fileUrl(j.zip_url)} data-testid={`job-zip-${j.id}`} className="inline-flex items-center gap-1 text-xs text-[#a8822e] hover:underline"><Download className="h-3.5 w-3.5" />ZIP</a>}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function History() {
  const api = useApi();
  const qc = useQueryClient();
  const { data: cat } = useCatalog();
  const [category, setCategory] = useState("all");
  const [mode, setMode] = useState("all");
  const params = { category: category === "all" ? undefined : category, mode: mode === "all" ? undefined : mode };
  const { data, isLoading } = useQuery({ queryKey: ["images", params], queryFn: () => api.get("/images", { params }).then((r) => r.data) });

  return (
    <div data-testid="history-page">
      <PageHeader eyebrow="Library" title="Gallery & history" subtitle="Every image you have generated, with its fidelity score and original." />
      <div className="px-6 py-8 lg:px-10">
        <Tabs defaultValue="images">
          <TabsList className="mb-6"><TabsTrigger value="images" data-testid="tab-images">Images</TabsTrigger><TabsTrigger value="jobs" data-testid="tab-jobs">Generation history</TabsTrigger></TabsList>
          <TabsContent value="images" className="space-y-6">
            <div className="flex flex-col gap-3 sm:flex-row">
              <div className="sm:w-56"><Field label="Jewellery type" value={category} onChange={setCategory} options={[{ id: "all", label: "All types" }, ...(cat?.categories || [])]} testid="gallery-filter-category" /></div>
              <div className="sm:w-56"><Field label="Tool" value={mode} onChange={setMode} options={MODES} testid="gallery-filter-mode" /></div>
            </div>
            {isLoading ? <Skeleton className="h-64" /> : data?.items.length ? (
              <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4" data-testid="gallery-grid">
                {data.items.map((img) => <ImageCard key={img.id} image={img} onChanged={() => qc.invalidateQueries({ queryKey: ["images"] })} />)}
              </div>
            ) : <EmptyState icon={ImageIcon} testid="gallery-empty" title="No images match" text="Try another filter or generate something new." />}
          </TabsContent>
          <TabsContent value="jobs"><JobsTable /></TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
