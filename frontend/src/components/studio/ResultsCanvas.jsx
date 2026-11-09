import { AlertTriangle, Download, Loader2, RotateCcw, Sparkles, Wand2 } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import ImageCard from "@/components/studio/ImageCard";
import { isRunning } from "@/components/studio/useGeneration";
import { fileUrl } from "@/lib/api";

function Running({ job }) {
  return (
    <div data-testid="job-running" className="mx-auto w-full max-w-xl space-y-6">
      <div className="shimmer relative aspect-[4/3] overflow-hidden rounded-lg border border-[#2a2622] bg-[#1b1815]">
        <img src={fileUrl(job.original_url)} alt="" className="h-full w-full object-contain opacity-40 blur-[2px]" />
      </div>
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm text-[#e8e2d6]">
          <span className="flex items-center gap-2" data-testid="job-stage"><Loader2 className="h-4 w-4 animate-spin text-[#c9a24b]" />{job.stage}</span>
          <span data-testid="job-progress">{job.progress}%</span>
        </div>
        <Progress value={job.progress} className="h-1 bg-[#2a2622] [&>div]:bg-[#c9a24b]" />
        <p className="text-xs text-[#8f877c]">Each image is generated, post-processed and inspected for design fidelity. This usually takes 20–60 seconds per image.</p>
      </div>
    </div>
  );
}

function Failures({ job, onRetry, retrying }) {
  if (!job.failures?.length) return null;
  return (
    <div data-testid="job-failures" className="flex flex-col gap-3 rounded-lg border border-[#5c2b2b] bg-[#2a1616] p-4 text-sm text-[#f3d1d1] sm:flex-row sm:items-center sm:justify-between">
      <div className="flex gap-2"><AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
        <span>{job.output_count - job.outputs.length} image(s) failed and {job.credits_refunded} credit(s) were refunded. <span className="opacity-70">{job.failures[0]}</span></span>
      </div>
      <Button data-testid="job-retry-btn" size="sm" variant="secondary" onClick={onRetry} disabled={retrying}><RotateCcw className="mr-1.5 h-3.5 w-3.5" />Retry</Button>
    </div>
  );
}

export default function ResultsCanvas({ job, gen, emptyTitle, emptyText, background, renderExtra }) {
  return (
    <div className="relative min-h-screen bg-[#141210] p-6 lg:p-10 grain">
      {!job && (
        <div data-testid="results-empty" className="flex h-full min-h-[60vh] flex-col items-start justify-end gap-3">
          <Sparkles className="h-6 w-6 text-[#c9a24b]" strokeWidth={1.4} />
          <h2 className="font-display text-4xl text-[#faf8f5]">{emptyTitle}</h2>
          <p className="max-w-md text-sm text-[#a39b8f]">{emptyText}</p>
        </div>
      )}
      {job && isRunning(job) && <Running job={job} />}
      {job && !isRunning(job) && (
        <div className="relative space-y-6" data-testid="job-results">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="eyebrow !text-[#c9a24b]">{job.status === "failed" ? "Generation failed" : "Your results"}</p>
              <p className="mt-1 text-sm text-[#a39b8f]" data-testid="job-credits-charged">
                {job.credits_charged} credit(s) charged · {job.provider}{job.is_mock && " · DEVELOPMENT MOCK"}
              </p>
            </div>
            <div className="flex gap-2">
              {job.zip_url && (
                <a href={fileUrl(job.zip_url)} data-testid="download-all-btn"
                  className="inline-flex items-center gap-1.5 rounded-md border border-[#3a342e] px-3 py-2 text-xs text-[#e8e2d6] transition-colors hover:border-[#c9a24b]">
                  <Download className="h-3.5 w-3.5" /> Download all
                </a>
              )}
              {job.mode !== "bg_removal" && job.outputs.length > 0 && (
                <button data-testid="regenerate-btn" onClick={() => gen.rerun.mutate(job.output_count)} disabled={gen.rerun.isPending}
                  className="inline-flex items-center gap-1.5 rounded-md bg-[#c9a24b] px-3 py-2 text-xs font-medium text-[#1c1917] transition-colors hover:bg-[#d8b45f] disabled:opacity-60">
                  <Wand2 className="h-3.5 w-3.5" /> New variations
                </button>
              )}
            </div>
          </div>
          <Failures job={job} retrying={gen.rerun.isPending} onRetry={() => gen.rerun.mutate(undefined)} />
          {renderExtra?.(job)}
          {job.outputs.length === 0 && job.status !== "failed" && (
            <p data-testid="results-all-deleted" className="text-sm text-[#a39b8f]">All images from this run were deleted. Upload a photo or adjust settings and generate again.</p>
          )}
          <div className={`grid gap-5 ${job.outputs.length > 1 ? "sm:grid-cols-2" : "max-w-2xl"}`}>
            {job.outputs.map((img) => <ImageCard key={img.id} image={img} onChanged={gen.refresh} background={background} large={job.outputs.length === 1} />)}
          </div>
        </div>
      )}
    </div>
  );
}
