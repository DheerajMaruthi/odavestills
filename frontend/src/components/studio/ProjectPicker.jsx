import { useQuery } from "@tanstack/react-query";
import { Field } from "@/components/studio/Controls";
import { useApi } from "@/lib/api";

export default function ProjectPicker({ value, onChange }) {
  const api = useApi();
  const { data: projects = [] } = useQuery({ queryKey: ["projects", ""], queryFn: () => api.get("/projects").then((r) => r.data) });
  const options = [{ id: "none", label: "No project" }, ...projects.map((p) => ({ id: p.id, label: p.name }))];
  return <Field label="Save results to project" value={value || "none"} onChange={(v) => onChange(v === "none" ? null : v)} options={options} testid="project-picker" />;
}
