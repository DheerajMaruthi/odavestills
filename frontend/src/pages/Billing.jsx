import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, FlaskConical, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { PageHeader } from "@/components/layout/PageHeader";
import { errMsg, formatDate, formatINR, useApi, useCatalog } from "@/lib/api";

const loadRazorpay = () =>
  new Promise((res) => {
    if (window.Razorpay) return res(true);
    const s = Object.assign(document.createElement("script"), { src: "https://checkout.razorpay.com/v1/checkout.js", onload: () => res(true), onerror: () => res(false) });
    document.body.appendChild(s);
  });

export const PlanCard = ({ plan, onBuy, busy, current }) => (
  <div data-testid={`plan-card-${plan.id}`} className={`flex flex-1 flex-col rounded-lg border bg-white p-7 ${plan.popular ? "border-[#c9a24b] shadow-md" : "border-[#ebe5da]"}`}>
    <div className="flex items-center justify-between"><p className="font-display text-2xl">{plan.name}</p>{plan.popular && <span className="rounded-full bg-[#f6efdc] px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-[#a8822e]">Most popular</span>}</div>
    <p className="mt-4 font-display text-5xl">{plan.price_paise ? formatINR(plan.price_paise) : "Free"}</p>
    <p className="mt-1 text-xs text-[#78716c]">{plan.credits} images{plan.price_paise ? ` · ${formatINR(Math.round(plan.price_paise / plan.credits))} per image` : ""}</p>
    <ul className="mt-6 flex-1 space-y-2.5 text-sm text-[#44403c]">{plan.features.map((f) => <li key={f} className="flex gap-2"><Check className="mt-0.5 h-4 w-4 shrink-0 text-[#a8822e]" />{f}</li>)}</ul>
    {onBuy && (
      <Button data-testid={`plan-buy-${plan.id}`} onClick={() => onBuy(plan)} disabled={!plan.purchasable || busy}
        className={`mt-7 w-full ${plan.popular ? "bg-[#c9a24b] text-[#1c1917] hover:bg-[#d8b45f]" : ""}`}>
        {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : !plan.purchasable ? (current ? "Current" : "Included at sign-up") : `Buy ${plan.credits} credits`}
      </Button>
    )}
  </div>
);

export default function Billing() {
  const api = useApi();
  const qc = useQueryClient();
  const { data: cat } = useCatalog();
  const { data, isLoading } = useQuery({ queryKey: ["billing"], queryFn: () => api.get("/billing/summary").then((r) => r.data) });
  const [busy, setBusy] = useState(null);
  const [demo, setDemo] = useState(null);
  const refresh = () => ["billing", "me", "dashboard"].forEach((k) => qc.invalidateQueries({ queryKey: [k] }));

  const buy = async (plan) => {
    setBusy(plan.id);
    try {
      const { data: order } = await api.post("/billing/orders", { plan_id: plan.id });
      if (order.mode === "demo") return setDemo(order);
      if (!(await loadRazorpay())) throw new Error("Could not load Razorpay checkout");
      new window.Razorpay({
        key: order.key_id, amount: order.amount, currency: order.currency, order_id: order.order_id, name: "AuraGem",
        description: `${plan.name} · ${plan.credits} credits`, prefill: order.prefill, theme: { color: "#1c1917" },
        handler: async (r) => {
          try {
            await api.post("/billing/verify", { order_id: r.razorpay_order_id, payment_id: r.razorpay_payment_id, signature: r.razorpay_signature });
            toast.success("Payment verified — credits added");
            refresh();
          } catch (e) { toast.error(errMsg(e)); }
        },
      }).open();
    } catch (e) {
      toast.error(errMsg(e));
    } finally {
      setBusy(null);
    }
  };

  const completeDemo = async () => {
    try {
      await api.post("/billing/demo-complete", { order_id: demo.order_id });
      toast.success(`DEMO: ${demo.plan.credits} credits added`);
      setDemo(null);
      refresh();
    } catch (e) { toast.error(errMsg(e)); }
  };

  const cancel = async () => {
    if (!window.confirm("Cancel your subscription? Remaining credits stay in your account.")) return;
    await api.post("/billing/cancel");
    toast.success("Subscription cancelled");
    refresh();
  };

  return (
    <div data-testid="billing-page">
      <PageHeader eyebrow="Account" title="Credits & billing" subtitle="One credit = one delivered image. Failed generations are refunded automatically." />
      <div className="space-y-12 px-6 py-8 lg:px-10">
        {data?.payments_mode === "demo" && (
          <div data-testid="payments-demo-banner" className="flex items-start gap-3 rounded-lg border border-[#f0dfb8] bg-[#fbf3e2] p-4 text-sm text-[#7c4a0b]">
            <FlaskConical className="mt-0.5 h-4 w-4 shrink-0" />
            <span><b>Demo payments mode.</b> Razorpay keys are not configured, so checkout is simulated and no money moves. Add RAZORPAY_KEY_ID / RAZORPAY_KEY_SECRET to enable real payments.</span>
          </div>
        )}
        {isLoading ? <Skeleton className="h-32" /> : (
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-lg bg-[#1c1917] p-7 text-[#faf8f5]">
              <p className="text-xs uppercase tracking-[0.16em] text-[#c9a24b]">Credit balance</p>
              <p data-testid="billing-credit-balance" className="mt-3 font-display text-6xl">{data.credits}</p>
            </div>
            <div className="rounded-lg border border-[#ebe5da] bg-white p-7 md:col-span-2">
              <p className="text-xs uppercase tracking-[0.16em] text-[#78716c]">Subscription</p>
              <p data-testid="billing-plan" className="mt-3 font-display text-4xl capitalize">{data.plan}</p>
              <p className="mt-1 text-sm text-[#78716c]">{data.subscription ? `Active · current period ends ${formatDate(data.subscription.renews_at)}` : "No active subscription"}</p>
              {data.subscription && <Button data-testid="cancel-subscription-btn" variant="outline" size="sm" className="mt-4" onClick={cancel}>Cancel subscription</Button>}
            </div>
          </div>
        )}
        <section className="space-y-5">
          <h2 className="font-display text-3xl">Plans</h2>
          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
            {cat?.plans.map((p) => <PlanCard key={p.id} plan={p} onBuy={buy} busy={busy === p.id} current={data?.plan === p.id} />)}
          </div>
        </section>
        <section className="space-y-5">
          <h2 className="font-display text-3xl">Transactions</h2>
          <div className="overflow-x-auto rounded-lg border border-[#ebe5da] bg-white" data-testid="transactions-table">
            <table className="w-full text-sm">
              <thead className="border-b border-[#efe9df] text-left text-xs uppercase tracking-[0.12em] text-[#78716c]"><tr><th className="px-5 py-3">Date</th><th className="px-5 py-3">Description</th><th className="px-5 py-3">Type</th><th className="px-5 py-3 text-right">Credits</th><th className="px-5 py-3 text-right">Balance</th></tr></thead>
              <tbody className="divide-y divide-[#efe9df]">
                {data?.transactions.map((t) => (
                  <tr key={t.id}><td className="px-5 py-3 text-xs text-[#78716c]">{formatDate(t.created_at)}</td><td className="px-5 py-3">{t.description}</td><td className="px-5 py-3 capitalize text-[#57534e]">{t.kind}</td>
                    <td className={`px-5 py-3 text-right ${t.amount > 0 ? "text-[#166534]" : ""}`}>{t.amount > 0 ? `+${t.amount}` : t.amount}</td><td className="px-5 py-3 text-right">{t.balance_after}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
      <Dialog open={!!demo} onOpenChange={(o) => !o && setDemo(null)}>
        <DialogContent data-testid="demo-checkout-dialog">
          <DialogHeader>
            <DialogTitle className="font-display text-2xl font-medium">Demo checkout</DialogTitle>
            <DialogDescription>DEMO MODE — no real payment is taken. This simulates a successful Razorpay payment so you can test the credit flow.</DialogDescription>
          </DialogHeader>
          {demo && <div className="rounded-md bg-[#f6efdc] p-4 text-sm"><b>{demo.plan.name}</b> · {demo.plan.credits} credits · {formatINR(demo.amount)}<p className="mt-1 text-xs text-[#78716c]">Order {demo.order_id}</p></div>}
          <Button data-testid="demo-pay-btn" onClick={completeDemo}>Simulate successful payment</Button>
        </DialogContent>
      </Dialog>
    </div>
  );
}
