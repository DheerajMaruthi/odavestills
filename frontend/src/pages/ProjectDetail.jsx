import { Link, useParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, ImageIcon, Sparkles } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import ImageCard from "@/components/studio/ImageCard";
import { PageHeader, EmptyState } from "@/components/layout/PageHeader";
import { useApi } from "@/lib/api";

export default function ProjectDetail() {
  const { id } = useParams();
  const api = useApi();
  const qc = useQueryClient();
  const project = useQuery({ queryKey: ["project", id], queryFn: () => api.get(`/projects/${id}`).then((r) => r.data) });
  const images = useQuery({ queryKey: ["images", { project_id: id }], queryFn: () => api.get("/images", { params: { project_id: id } }).then((r) => r.data) });
  const refresh = () => { qc.invalidateQueries({ queryKey: ["images"] }); qc.invalidateQueries({ queryKey: ["project", id] }); };

  if (project.isError) return <div className="p-10"><EmptyState title="Project not found" action={<Link to="/app/projects" className="text-sm underline">Back to projects</Link>} /></div>;

  return (
    <div data-testid="project-detail-page">
      <PageHeader eyebrow={<Link to="/app/projects" className="inline-flex items-center gap-1" data-testid="back-to-projects"><ArrowLeft className="h-3 w-3" /> Projects</Link>}
        title={project.data?.name || "…"} subtitle={project.data?.description || `${project.data?.image_count ?? 0} images`}
        actions={<Link to={`/app/studio?project=${id}`} data-testid="project-generate-btn" className="inline-flex items-center gap-2 rounded-md bg-[#1c1917] px-5 py-3 text-sm text-[#faf8f5] hover:bg-[#2c2724]"><Sparkles className="h-4 w-4 text-[#e2c47e]" />Generate into project</Link>} />
      <div className="px-6 py-8 lg:px-10">
        {images.isLoading ? <Skeleton className="h-64" /> : images.data?.items.length ? (
          <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">{images.data.items.map((img) => <ImageCard key={img.id} image={img} onChanged={refresh} />)}</div>
        ) : <EmptyState icon={ImageIcon} testid="project-images-empty" title="This project is empty" text="Generate images into it, or use “Save to project” on any result." />}
      </div>
    </div>
  );
}
