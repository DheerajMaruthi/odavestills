import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useUser } from "@clerk/react";
import { ArrowUpRight, FolderOpen, Gem, ImageIcon, Scissors, UserRound, Upload } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { PageHeader, EmptyState } from "@/components/layout/PageHeader";
import { fileUrl, formatDate, useApi } from "@/lib/api";

const STATUS = { completed: "text-[#166534] bg-[#ecf5ee]", partial: "text-[#92400e] bg-[#fbf3e2]", failed: "text-[#991b1b] bg-[#fbeaea]", processing: "text-[#1e40af] bg-[#eef2fb]", queued: "text-[#57534e] bg-[#f3f1ee]" };
const MODE = { product: "Product", model: "Model", bg_removal: "Cut-out" };
export const StatusPill = ({ status, testid }) => <span data-testid={testid} className={`rounded-full px-2.5 py-0.5 text-[11px] font-medium capitalize ${STATUS[status]}`}>{status}</span>;

const Stat = ({ label, value, testid }) => (
  <div className="rounded-lg border border-[#ebe5da] bg-white p-6">
    <p className="text-xs uppercase tracking-[0.16em] text-[#78716c]">{label}</p>
    <p data-testid={testid} className="mt-3 font-display text-5xl text-[#1c1917]">{value}</p>
  </div>
);

const ACTIONS = [
  { to: "/app/studio", title: "Product studio", text: "Catalogue-grade shots", icon: Gem, id: "studio" },
  { to: "/app/model", title: "Model photography", text: "Jewellery on AI models", icon: UserRound, id: "model" },
  { to: "/app/background", title: "Remove background", text: "Transparent PNG", icon: Scissors, id: "background" },
  { to: "/app/projects", title: "Projects", text: "Organise collections", icon: FolderOpen, id: "projects" },
];

export default function Dashboard() {
  const api = useApi();
  const { user } = useUser();
  const { data, isLoading } = useQuery({ queryKey: ["dashboard"], queryFn: () => api.get("/dashboard").then((r) => r.data), refetchInterval: 10000 });
  const st = data?.stats;

  return (
    <div data-testid="dashboard-page">
      <PageHeader eyebrow="Dashboard" title={`Welcome${user?.firstName ? `, ${user.firstName}` : ""}.`}
        subtitle="Your jewellery studio at a glance."
        actions={<Link to="/app/studio" data-testid="quick-upload-btn" className="inline-flex items-center gap-2 rounded-md bg-[#1c1917] px-5 py-3 text-sm font-medium text-[#faf8f5] transition-colors hover:bg-[#2c2724]"><Upload className="h-4 w-4" />Upload a photo</Link>} />
      <div className="space-y-12 px-6 py-10 lg:px-10">
        {isLoading ? <Skeleton className="h-32 w-full" /> : (
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <Stat label="Images generated" value={st.total_generated} testid="stat-total-generated" />
            <Stat label="Credits available" value={st.credits} testid="stat-credits" />
            <Stat label="Projects" value={st.projects} testid="stat-projects" />
            <div className="rounded-lg border border-[#e8dfcc] bg-[#f6efdc]/60 p-6">
              <p className="text-xs uppercase tracking-[0.16em] text-[#a8822e]">Subscription</p>
              <p data-testid="stat-plan" className="mt-3 font-display text-4xl capitalize text-[#1c1917]">{st.plan}</p>
              <p className="mt-1 text-xs text-[#78716c]">{data.subscription?.renews_at ? `Renews ${formatDate(data.subscription.renews_at)}` : "Trial credits"} · <Link to="/app/billing" className="underline" data-testid="dashboard-billing-link">Manage</Link></p>
            </div>
          </div>
        )}

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {ACTIONS.map(({ to, title, text, icon: Icon, id }) => (
            <Link key={to} to={to} data-testid={`quick-action-${id}`} className="group flex items-start justify-between rounded-lg border border-[#ebe5da] bg-white p-5 transition-shadow hover:shadow-md">
              <div><Icon className="h-5 w-5 text-[#a8822e]" strokeWidth={1.5} /><p className="mt-4 font-medium text-[#1c1917]">{title}</p><p className="text-xs text-[#78716c]">{text}</p></div>
              <ArrowUpRight className="h-4 w-4 text-[#a8a29e] transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5" />
            </Link>
          ))}
        </div>

        <section className="space-y-4">
          <div className="flex items-end justify-between"><h2 className="font-display text-3xl">Recent generations</h2><Link to="/app/history" className="text-sm text-[#a8822e] underline-offset-4 hover:underline" data-testid="view-all-images">View all</Link></div>
          {data?.recent_images?.length ? (
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
              {data.recent_images.map((img) => (
                <div key={img.id} className={`overflow-hidden rounded-lg border border-[#ebe5da] ${img.content_type === "image/png" ? "checkerboard" : "bg-[#f3efe8]"}`} data-testid={`recent-image-${img.id}`}>
                  <img src={fileUrl(img.url)} alt={img.category} className="aspect-square w-full object-contain" loading="lazy" />
                </div>
              ))}
            </div>
          ) : !isLoading && <EmptyState icon={ImageIcon} testid="recent-images-empty" title="No images yet" text="Your first three images are on us." action={<Link to="/app/studio" className="text-sm text-[#a8822e] underline">Open the studio</Link>} />}
        </section>

        <div className="grid gap-8 xl:grid-cols-2">
          <section className="space-y-4">
            <h2 className="font-display text-3xl">Generation status</h2>
            <div className="divide-y divide-[#efe9df] rounded-lg border border-[#ebe5da] bg-white" data-testid="recent-jobs">
              {data?.recent_jobs?.length ? data.recent_jobs.map((j) => (
                <div key={j.id} className="flex items-center justify-between px-5 py-3.5 text-sm" data-testid={`recent-job-${j.id}`}>
                  <span><span className="font-medium">{MODE[j.mode]}</span> <span className="text-[#78716c]">· {j.category} · {j.output_count} image(s)</span></span>
                  <span className="flex items-center gap-3"><span className="hidden text-xs text-[#a8a29e] sm:inline">{formatDate(j.created_at)}</span><StatusPill status={j.status} testid={`recent-job-status-${j.id}`} /></span>
                </div>
              )) : <p className="px-5 py-6 text-sm text-[#78716c]">No generations yet.</p>}
            </div>
          </section>
          <section className="space-y-4">
            <h2 className="font-display text-3xl">Usage history</h2>
            <div className="divide-y divide-[#efe9df] rounded-lg border border-[#ebe5da] bg-white" data-testid="usage-history">
              {data?.transactions?.map((t) => (
                <div key={t.id} className="flex items-center justify-between px-5 py-3.5 text-sm">
                  <span>{t.description}<span className="ml-2 text-xs text-[#a8a29e]">{formatDate(t.created_at)}</span></span>
                  <span className={t.amount > 0 ? "text-[#166534]" : "text-[#44403c]"}>{t.amount > 0 ? `+${t.amount}` : t.amount}</span>
                </div>
              ))}
            </div>
          </section>
        </div>

        {data?.recent_projects?.length > 0 && (
          <section className="space-y-4">
            <h2 className="font-display text-3xl">Recent projects</h2>
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {data.recent_projects.map((p) => (
                <Link key={p.id} to={`/app/projects/${p.id}`} data-testid={`recent-project-${p.id}`} className="rounded-lg border border-[#ebe5da] bg-white p-5 transition-shadow hover:shadow-md">
                  <p className="font-medium">{p.name}</p><p className="text-xs text-[#78716c]">{p.image_count} images</p>
                </Link>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
