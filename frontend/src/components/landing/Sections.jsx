import { Camera, FolderOpen, Layers, Scissors, ShieldCheck, UserRound, Wallet } from "lucide-react";
import { useCatalog } from "@/lib/api";

const Section = ({ id, eyebrow, title, text, children, className = "" }) => (
  <section id={id} className={`mx-auto max-w-7xl px-6 py-24 lg:px-10 ${className}`}>
    <div className="max-w-2xl">
      <p className="eyebrow">{eyebrow}</p>
      <h2 className="mt-4 font-display text-4xl font-medium leading-tight text-[#1c1917] sm:text-5xl">{title}</h2>
      {text && <p className="mt-4 text-base text-[#57534e]">{text}</p>}
    </div>
    <div className="mt-14">{children}</div>
  </section>
);

const STEPS = [
  { n: "01", t: "Photograph it simply", d: "Any phone, any table. Good light helps — perfection doesn’t matter.", img: "/showcase/ring-before.jpg" },
  { n: "02", t: "Choose the look", d: "Pick the jewellery type, a style or a model, then fine-tune lighting, angle and format.", img: "https://images.unsplash.com/photo-1724937798320-d0c4fac1787d?auto=format&fit=crop&w=800&q=70" },
  { n: "03", t: "Review & download", d: "Compare against your original, read the fidelity score, and export in full resolution.", img: "/showcase/ring-after.jpg" },
];

export function HowItWorks() {
  return (
    <Section id="how" eyebrow="How it works" title="From counter-top snapshot to campaign in under a minute.">
      <div className="grid gap-10 md:grid-cols-3">
        {STEPS.map((s) => (
          <div key={s.n} className="group" data-testid={`how-step-${s.n}`}>
            <div className="overflow-hidden rounded-lg"><img src={s.img} alt="" className="aspect-[4/3] w-full object-cover transition-transform duration-700 group-hover:scale-105" /></div>
            <p className="mt-6 font-display text-xl italic text-[#a8822e]">{s.n}</p>
            <h3 className="mt-1 text-lg font-semibold text-[#1c1917]">{s.t}</h3>
            <p className="mt-2 text-sm leading-relaxed text-[#57534e]">{s.d}</p>
          </div>
        ))}
      </div>
    </Section>
  );
}

const FEATURES = [
  { icon: ShieldCheck, t: "Pixel-exact jewellery", d: "Your real piece is cut out with an AI matte and placed, untouched, into an AI-built studio set, so every stone, prong and engraving stays yours. AI re-shoots are inspected and retried until they pass.", span: "md:col-span-7", dark: true },
  { icon: UserRound, t: "AI model photography", d: "Bridal, South Indian, festive or editorial looks without a shoot.", span: "md:col-span-5" },
  { icon: Scissors, t: "Clean cut-outs", d: "Transparent PNGs for marketplaces and websites, with instant background swaps.", span: "md:col-span-4" },
  { icon: Layers, t: "Up to 4 variations", d: "Explore compositions in one run, regenerate with a click.", span: "md:col-span-4" },
  { icon: FolderOpen, t: "Projects & history", d: "Organise by collection; filter by jewellery type; download as ZIP.", span: "md:col-span-4" },
  { icon: Wallet, t: "Fair credits", d: "One credit per delivered image. Failures are refunded automatically.", span: "md:col-span-6" },
  { icon: Camera, t: "Built for Indian jewellery", d: "Kundan, temple, polki and meenakari aware prompts and presets.", span: "md:col-span-6" },
];

export function Features() {
  return (
    <div className="bg-[#f3efe8]">
      <Section eyebrow="Why AuraGem" title="Beautiful is easy. Faithful is the point.">
        <div className="grid gap-5 md:grid-cols-12">
          {FEATURES.map(({ icon: Icon, t, d, span, dark }) => (
            <div key={t} className={`${span} rounded-lg p-8 transition-shadow hover:shadow-lg ${dark ? "bg-[#1c1917] text-[#faf8f5]" : "border border-[#e4ded4] bg-white"}`}>
              <Icon className={`h-6 w-6 ${dark ? "text-[#e2c47e]" : "text-[#a8822e]"}`} strokeWidth={1.5} />
              <h3 className={`mt-6 font-display text-2xl ${dark ? "" : "text-[#1c1917]"}`}>{t}</h3>
              <p className={`mt-2 max-w-md text-sm leading-relaxed ${dark ? "text-[#c9c1b4]" : "text-[#57534e]"}`}>{d}</p>
            </div>
          ))}
        </div>
      </Section>
    </div>
  );
}

export function Styles() {
  const { data: cat } = useCatalog();
  return (
    <Section id="styles" eyebrow="Photography styles" title="Eleven sets, one click each." text="From luxury black to royal Indian heritage — every preset is tuned for metal, stones and sparkle.">
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        {cat?.styles.map((s, i) => (
          <div key={s.id} data-testid={`landing-style-${s.id}`} className={`group relative overflow-hidden rounded-lg ${i === 0 ? "sm:col-span-2 sm:row-span-2" : ""}`}>
            <div className="h-full min-h-[140px] transition-transform duration-700 group-hover:scale-105" style={{ background: s.swatch[0] }}>
              <div className="absolute inset-y-0 right-0 w-2/5 opacity-80" style={{ background: s.swatch[1] }} />
            </div>
            <span className="absolute bottom-3 left-4 rounded bg-white/90 px-2.5 py-1 text-xs font-medium text-[#1c1917]">{s.label}</span>
          </div>
        ))}
      </div>
    </Section>
  );
}

const MODELS = [
  ["Traditional Indian Bridal", "https://images.unsplash.com/photo-1600685890506-593fdf55949b?auto=format&fit=crop&w=900&q=75"],
  ["South Indian Traditional", "https://images.unsplash.com/photo-1688382654723-a7366006519b?auto=format&fit=crop&w=900&q=75"],
  ["Festive", "https://images.unsplash.com/photo-1778148046574-c1509f5a40d4?auto=format&fit=crop&w=900&q=75"],
];

export function Models() {
  return (
    <div className="bg-[#141210] text-[#faf8f5] grain relative">
      <Section id="models" eyebrow="AI model photography" title={<span className="text-[#faf8f5]">Your piece, worn by the right face.</span>}>
        <p className="-mt-10 mb-12 max-w-xl text-sm text-[#a39b8f]">Choose gender, appearance, pose, clothing and setting. Presets for traditional bridal, South Indian, North Indian bridal, modern fashion, festive and luxury editorial. Reference imagery shown below is illustrative.</p>
        <div className="grid gap-5 md:grid-cols-3">
          {MODELS.map(([t, src], i) => (
            <div key={t} className={`group relative overflow-hidden rounded-lg ${i === 1 ? "md:translate-y-10" : ""}`}>
              <img src={src} alt={t} className="aspect-[3/4] w-full object-cover transition-transform duration-700 group-hover:scale-105" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent" />
              <p className="absolute bottom-5 left-5 font-display text-2xl">{t}</p>
            </div>
          ))}
        </div>
      </Section>
    </div>
  );
}

export { Section };
