import { useState } from "react";
import { NavLink, Outlet, Link } from "react-router-dom";
import { UserButton } from "@clerk/react";
import { LayoutGrid, Gem, UserRound, Scissors, FolderOpen, History, CreditCard, Menu, Coins, FlaskConical } from "lucide-react";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Logo } from "@/components/brand/Logo";
import { useMe } from "@/lib/api";

const NAV = [
  { to: "/app", label: "Dashboard", icon: LayoutGrid, end: true, id: "dashboard" },
  { to: "/app/studio", label: "Product Studio", icon: Gem, id: "studio" },
  { to: "/app/model", label: "Model Photography", icon: UserRound, id: "model" },
  { to: "/app/background", label: "Background Removal", icon: Scissors, id: "background" },
  { to: "/app/projects", label: "Projects", icon: FolderOpen, id: "projects" },
  { to: "/app/history", label: "Gallery & History", icon: History, id: "history" },
  { to: "/app/billing", label: "Credits & Billing", icon: CreditCard, id: "billing" },
];

function NavItems({ onNavigate }) {
  return (
    <nav className="flex flex-col gap-0.5">
      {NAV.map(({ to, label, icon: Icon, end, id }) => (
        <NavLink key={to} to={to} end={end} onClick={onNavigate} data-testid={`nav-${id}`}
          className={({ isActive }) => `flex items-center gap-3 rounded-md px-3 py-2.5 text-sm transition-colors ${
            isActive ? "bg-[#1c1917] text-[#faf8f5]" : "text-[#44403c] hover:bg-[#f0ebe2]"}`}>
          <Icon className="h-4 w-4" strokeWidth={1.6} />
          {label}
        </NavLink>
      ))}
    </nav>
  );
}

function CreditsCard() {
  const { data } = useMe();
  return (
    <Link to="/app/billing" data-testid="sidebar-credits" className="block rounded-lg border border-[#e8dfcc] bg-[#f6efdc]/60 p-4 transition-colors hover:bg-[#f6efdc]">
      <div className="flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-[#a8822e]"><Coins className="h-3.5 w-3.5" /> Credits</div>
      <div className="mt-1 font-display text-3xl text-[#1c1917]" data-testid="sidebar-credit-balance">{data?.credits ?? "–"}</div>
      <div className="text-xs capitalize text-[#78716c]">{data?.plan || "free"} plan · top up</div>
    </Link>
  );
}

function MockBanner() {
  const { data } = useMe();
  if (data?.ai_mode !== "mock") return null;
  return (
    <div data-testid="mock-mode-banner" className="flex items-center gap-2 bg-[#1c1917] px-6 py-2 text-xs text-[#e2c47e]">
      <FlaskConical className="h-3.5 w-3.5" /> DEVELOPMENT MOCK MODE — images are not AI generated. Configure an AI key to enable real generation.
    </div>
  );
}

export default function AppShell() {
  const [open, setOpen] = useState(false);
  return (
    <div className="min-h-screen bg-[#faf8f5]">
      <aside className="fixed inset-y-0 left-0 hidden w-64 flex-col justify-between border-r border-[#ebe5da] bg-[#fbf9f6] px-4 py-6 lg:flex">
        <div className="space-y-8">
          <div className="px-2"><Logo to="/app" /></div>
          <NavItems />
        </div>
        <div className="space-y-4">
          <CreditsCard />
          <div className="flex items-center gap-3 px-2"><UserButton /><span className="text-xs text-[#78716c]">Account</span></div>
        </div>
      </aside>
      <div className="lg:pl-64">
        <header className="sticky top-0 z-30 flex items-center justify-between border-b border-[#ebe5da] bg-[#faf8f5]/90 px-4 py-3 backdrop-blur lg:hidden">
          <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger asChild>
              <button data-testid="mobile-menu-btn" className="rounded-md p-2 hover:bg-[#f0ebe2]" aria-label="Open menu"><Menu className="h-5 w-5" /></button>
            </SheetTrigger>
            <SheetContent side="left" className="w-72 bg-[#fbf9f6]">
              <div className="mb-8 mt-2"><Logo to="/app" /></div>
              <NavItems onNavigate={() => setOpen(false)} />
              <div className="mt-8"><CreditsCard /></div>
            </SheetContent>
          </Sheet>
          <Logo to="/app" />
          <UserButton />
        </header>
        <MockBanner />
        <main><Outlet /></main>
      </div>
    </div>
  );
}
