import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Logo } from "@/components/brand/Logo";
import { PlanCard } from "@/pages/Billing";
import { Section } from "@/components/landing/Sections";
import { useCatalog } from "@/lib/api";

export function Pricing() {
  const { data: cat } = useCatalog();
  return (
    <Section id="pricing" eyebrow="Pricing" title="Pay per delivered image." text="Start with 3 free images. Buy a pack when you need more — failed generations never cost you a credit.">
      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {cat?.plans.map((p) => (
          <div key={p.id} className="flex flex-col">
            <PlanCard plan={p} />
            <Link to="/sign-up" data-testid={`landing-plan-cta-${p.id}`} className="mt-3 text-center text-sm text-[#a8822e] underline-offset-4 hover:underline">{p.price_paise ? "Get started" : "Start free"}</Link>
          </div>
        ))}
      </div>
      <p className="mt-6 text-xs text-[#78716c]">Prices in INR, inclusive of platform fees. Secure payments by Razorpay.</p>
    </Section>
  );
}

const QUOTES = [
  ["We shot 140 bridal pieces in an afternoon. The fidelity score told us exactly which three to re-check.", "Retail jeweller, Jaipur"],
  ["The South Indian preset finally looks like our customers — temple jewellery, jasmine and all.", "Wholesaler, Coimbatore"],
  ["Transparent cut-outs went straight onto our marketplace listings. No retoucher needed.", "D2C brand founder, Mumbai"],
];

export function Testimonials() {
  return (
    <div className="bg-[#f3efe8]">
      <Section eyebrow="Testimonials" title="What jewellers tell us." text="Sample testimonials — illustrative content for this preview, not real customer reviews.">
        <div className="grid gap-5 md:grid-cols-3" data-testid="testimonials">
          {QUOTES.map(([q, who]) => (
            <figure key={who} className="rounded-lg border border-[#e4ded4] bg-white p-8">
              <span className="rounded bg-[#f3f1ee] px-2 py-0.5 text-[10px] uppercase tracking-wider text-[#78716c]">Sample</span>
              <blockquote className="mt-5 font-display text-2xl leading-snug text-[#1c1917]">“{q}”</blockquote>
              <figcaption className="mt-6 text-xs uppercase tracking-[0.16em] text-[#a8822e]">{who}</figcaption>
            </figure>
          ))}
        </div>
      </Section>
    </div>
  );
}

const FAQ = [
  ["Which jewellery can I upload?", "Necklaces, earrings, rings, bangles, bracelets, pendants, full sets and more. Gold, silver, diamond, kundan, polki and temple jewellery all work."],
  ["What photo should I upload?", "One piece (or one set), in focus, evenly lit, on a plain surface. JPEG, PNG or WebP up to 15 MB and at least 256px on each side."],
  ["Will the AI change my design?", "Not in Pixel-exact mode: the jewellery in the final image is your own photo's pixels, cut out precisely, with AI creating only the studio set, light and shadow. AI re-shoot and model photography re-render the piece for a fuller studio look. There, every image is inspected against your original and regenerated if fidelity is low, with a score and any issues shown. Always review before publishing."],
  ["What are credits?", "One credit equals one delivered image. Credits are reserved when you start and automatically refunded for any image that fails."],
  ["How long does it take?", "Usually 20–60 seconds per image, including the quality check."],
  ["Can I use the images commercially?", "Yes. Images you generate are yours to use on your website, marketplaces, social media and print."],
  ["Are my photos private?", "Uploads and results are stored privately and served only through expiring, signed links tied to your account."],
];

export function Faq() {
  return (
    <Section id="faq" eyebrow="Questions" title="Frequently asked.">
      <Accordion type="single" collapsible className="max-w-3xl" data-testid="faq-accordion">
        {FAQ.map(([q, a], i) => (
          <AccordionItem key={q} value={`q${i}`}>
            <AccordionTrigger data-testid={`faq-item-${i}`} className="text-left font-display text-xl font-medium hover:no-underline">{q}</AccordionTrigger>
            <AccordionContent className="text-sm leading-relaxed text-[#57534e]">{a}</AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </Section>
  );
}

export function FinalCta() {
  return (
    <section className="mx-auto max-w-7xl px-6 pb-24 lg:px-10">
      <div className="relative overflow-hidden rounded-lg bg-[#1c1917] px-8 py-16 text-[#faf8f5] sm:px-16 grain">
        <img src="/showcase/ring-cutout.png" alt="" className="pointer-events-none absolute -right-10 bottom-0 hidden h-[110%] opacity-90 md:block" />
        <p className="eyebrow !text-[#e2c47e]">Begin</p>
        <h2 className="mt-4 max-w-xl font-display text-4xl leading-tight sm:text-5xl">Your next collection deserves its own studio.</h2>
        <Link to="/sign-up" data-testid="final-cta-btn" className="mt-10 inline-flex items-center gap-2 rounded-md bg-[#c9a24b] px-7 py-4 text-sm font-medium text-[#1c1917] transition-colors hover:bg-[#d8b45f]">
          Create 3 free images <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </section>
  );
}

export function Footer() {
  return (
    <footer className="border-t border-[#ebe5da]">
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-6 py-10 text-sm text-[#78716c] sm:flex-row sm:items-center sm:justify-between lg:px-10">
        <Logo />
        <p>© {new Date().getFullYear()} AuraGem. AI jewellery photography for India.</p>
      </div>
    </footer>
  );
}
