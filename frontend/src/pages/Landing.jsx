import { Nav, Hero, Marquee } from "@/components/landing/Hero";
import { HowItWorks, Features, Styles, Models } from "@/components/landing/Sections";
import { Pricing, Testimonials, Faq, FinalCta, Footer } from "@/components/landing/Closing";

export default function Landing() {
  return (
    <div className="min-h-screen bg-[#faf8f5]" data-testid="landing-page">
      <Nav />
      <Hero />
      <Marquee />
      <HowItWorks />
      <Features />
      <Styles />
      <Models />
      <Pricing />
      <Testimonials />
      <Faq />
      <FinalCta />
      <Footer />
    </div>
  );
}
