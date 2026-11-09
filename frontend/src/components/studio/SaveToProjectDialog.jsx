import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { errMsg, useApi } from "@/lib/api";

export default function SaveToProjectDialog({ image, open, onOpenChange, onSaved }) {
  const api = useApi();
  const qc = useQueryClient();
  const [name, setName] = useState("");
  const { data: projects = [] } = useQuery({ queryKey: ["projects", ""], queryFn: () => api.get("/projects").then((r) => r.data), enabled: open });

  const save = async (projectId) => {
    try {
      await api.patch(`/images/${image.id}`, { project_id: projectId });
      toast.success("Saved to project");
      qc.invalidateQueries({ queryKey: ["projects"] });
      onSaved?.();
      onOpenChange(false);
    } catch (e) {
      toast.error(errMsg(e));
    }
  };

  const createAndSave = async () => {
    if (!name.trim()) return;
    try {
      const { data } = await api.post("/projects", { name: name.trim(), category: image.category });
      setName("");
      await save(data.id);
    } catch (e) {
      toast.error(errMsg(e));
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent data-testid="save-project-dialog" className="max-w-md">
        <DialogHeader><DialogTitle className="font-display text-2xl font-medium">Save to project</DialogTitle></DialogHeader>
        <div className="max-h-64 space-y-1.5 overflow-y-auto">
          {projects.length === 0 && <p className="text-sm text-[#78716c]">No projects yet — create one below.</p>}
          {projects.map((p) => (
            <button key={p.id} data-testid={`save-project-option-${p.id}`} onClick={() => save(p.id)}
              className={`flex w-full items-center justify-between rounded-md border px-3 py-2.5 text-left text-sm transition-colors hover:border-[#c9a24b] ${
                image?.project_id === p.id ? "border-[#c9a24b] bg-[#f6efdc]" : "border-[#e4ded4]"}`}>
              <span>{p.name}</span><span className="text-xs text-[#78716c]">{p.image_count} images</span>
            </button>
          ))}
        </div>
        <div className="flex gap-2 border-t border-[#efe9df] pt-4">
          <Input data-testid="save-project-new-name" placeholder="New project name" value={name} onChange={(e) => setName(e.target.value)} />
          <Button data-testid="save-project-create-btn" onClick={createAndSave}>Create</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
