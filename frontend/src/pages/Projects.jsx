import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { FolderOpen, Plus, Search, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Field } from "@/components/studio/Controls";
import { PageHeader, EmptyState } from "@/components/layout/PageHeader";
import { errMsg, fileUrl, labelOf, useApi, useCatalog } from "@/lib/api";

function NewProject({ categories, onCreated }) {
  const api = useApi();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: "", description: "", category: "none" });
  const create = async () => {
    try {
      await api.post("/projects", { ...form, category: form.category === "none" ? null : form.category });
      toast.success("Project created");
      setForm({ name: "", description: "", category: "none" });
      setOpen(false);
      onCreated();
    } catch (e) {
      toast.error(errMsg(e));
    }
  };
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild><Button data-testid="new-project-btn"><Plus className="mr-1.5 h-4 w-4" />New project</Button></DialogTrigger>
      <DialogContent data-testid="new-project-dialog">
        <DialogHeader><DialogTitle className="font-display text-2xl font-medium">New project</DialogTitle></DialogHeader>
        <div className="space-y-3">
          <Input data-testid="project-name-input" placeholder="e.g. Diwali bridal collection" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <Textarea data-testid="project-description-input" placeholder="Description (optional)" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          <Field label="Jewellery type" value={form.category} onChange={(v) => setForm({ ...form, category: v })} options={[{ id: "none", label: "Mixed" }, ...(categories || [])]} testid="project-category-select" />
          <Button data-testid="project-create-submit" className="w-full" disabled={!form.name.trim()} onClick={create}>Create project</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

export default function Projects() {
  const api = useApi();
  const qc = useQueryClient();
  const { data: cat } = useCatalog();
  const [q, setQ] = useState("");
  const [category, setCategory] = useState("all");
  const { data: projects, isLoading } = useQuery({
    queryKey: ["projects", q, category],
    queryFn: () => api.get("/projects", { params: { q, category: category === "all" ? undefined : category } }).then((r) => r.data),
  });
  const refresh = () => qc.invalidateQueries({ queryKey: ["projects"] });

  const remove = async (p) => {
    if (!window.confirm(`Delete project "${p.name}"? Its images stay in your gallery.`)) return;
    try {
      await api.delete(`/projects/${p.id}`);
      toast.success("Project deleted");
      refresh();
    } catch (e) {
      toast.error(errMsg(e));
    }
  };

  return (
    <div data-testid="projects-page">
      <PageHeader eyebrow="Library" title="Projects" subtitle="Group photographs by collection, client or catalogue." actions={<NewProject categories={cat?.categories} onCreated={refresh} />} />
      <div className="space-y-8 px-6 py-8 lg:px-10">
        <div className="flex flex-col gap-3 sm:flex-row">
          <div className="relative flex-1 sm:max-w-sm">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#a8a29e]" />
            <Input data-testid="project-search-input" className="bg-white pl-9" placeholder="Search projects" value={q} onChange={(e) => setQ(e.target.value)} />
          </div>
          <div className="sm:w-56"><Field label="" value={category} onChange={setCategory} options={[{ id: "all", label: "All jewellery types" }, ...(cat?.categories || [])]} testid="project-filter-category" /></div>
        </div>
        {isLoading ? <Skeleton className="h-48" /> : projects?.length ? (
          <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
            {projects.map((p) => (
              <div key={p.id} className="group overflow-hidden rounded-lg border border-[#ebe5da] bg-white transition-shadow hover:shadow-md" data-testid={`project-card-${p.id}`}>
                <Link to={`/app/projects/${p.id}`} data-testid={`project-open-${p.id}`} className="block aspect-[16/10] bg-[#f3efe8]">
                  {p.cover_url ? <img src={fileUrl(p.cover_url)} alt="" className="h-full w-full object-cover" /> : <div className="flex h-full items-center justify-center"><FolderOpen className="h-8 w-8 text-[#c9b99a]" strokeWidth={1.2} /></div>}
                </Link>
                <div className="flex items-start justify-between p-5">
                  <div>
                    <p className="font-medium text-[#1c1917]">{p.name}</p>
                    <p className="text-xs text-[#78716c]">{p.image_count} images{p.category && ` · ${labelOf(cat?.categories, p.category)}`}</p>
                  </div>
                  <button data-testid={`project-delete-${p.id}`} onClick={() => remove(p)} className="rounded p-1.5 text-[#a8a29e] hover:bg-[#fbeaea] hover:text-[#b91c1c]" aria-label="Delete project"><Trash2 className="h-4 w-4" /></button>
                </div>
              </div>
            ))}
          </div>
        ) : <EmptyState icon={FolderOpen} testid="projects-empty" title={q || category !== "all" ? "No matching projects" : "No projects yet"} text="Create a project for each collection to keep your photographs organised." />}
      </div>
    </div>
  );
}
