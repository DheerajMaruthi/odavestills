import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { errMsg, useApi } from "@/lib/api";

const RUNNING = ["queued", "processing"];
export const isRunning = (job) => RUNNING.includes(job?.status);

export function useGeneration() {
  const api = useApi();
  const qc = useQueryClient();
  const [jobId, setJobId] = useState(null);

  const jobQuery = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => api.get(`/jobs/${jobId}`).then((r) => r.data),
    enabled: !!jobId,
    refetchInterval: (q) => (isRunning(q.state.data) ? 2500 : false),
  });
  const job = jobQuery.data;

  useEffect(() => {
    if (!job || isRunning(job)) return;
    qc.invalidateQueries({ queryKey: ["me"] });
    qc.invalidateQueries({ queryKey: ["dashboard"] });
    if (job.status === "completed") toast.success(`${job.outputs.length} image(s) ready`);
    if (job.status === "partial") toast.warning("Some images failed — their credits were refunded");
    if (job.status === "failed") toast.error("Generation failed — credits refunded");
  }, [job?.id, job?.status]); // eslint-disable-line react-hooks/exhaustive-deps

  const onStarted = (data) => {
    qc.setQueryData(["job", data.id], data);
    setJobId(data.id);
    qc.invalidateQueries({ queryKey: ["me"] });
  };

  const submit = useMutation({
    mutationFn: (payload) => api.post("/jobs", payload).then((r) => r.data),
    onSuccess: onStarted,
    onError: (e) => toast.error(errMsg(e)),
  });

  const rerun = useMutation({
    mutationFn: (count) => api.post(`/jobs/${jobId}/rerun`, { output_count: count }).then((r) => r.data),
    onSuccess: onStarted,
    onError: (e) => toast.error(errMsg(e)),
  });

  const refresh = () => qc.invalidateQueries({ queryKey: ["job", jobId] });
  return { job, submit, rerun, refresh, reset: () => setJobId(null) };
}
