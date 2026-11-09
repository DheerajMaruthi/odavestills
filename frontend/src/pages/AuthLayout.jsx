import { Logo } from "@/components/brand/Logo";

export default function AuthLayout({ children }) {
  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="relative hidden overflow-hidden bg-[#141210] lg:flex lg:flex-col lg:justify-between lg:p-12 grain">
        <Logo light />
        <img src="https://images.unsplash.com/photo-1600685890506-593fdf55949b?auto=format&fit=crop&w=1200&q=80"
          alt="Bride wearing gold jewellery" className="absolute inset-0 h-full w-full object-cover opacity-55" />
        <div className="relative max-w-md">
          <p className="eyebrow !text-[#e2c47e]">AI jewellery studio</p>
          <h2 className="mt-4 font-display text-5xl leading-tight text-[#faf8f5]">Every piece deserves a portrait worthy of it.</h2>
        </div>
      </div>
      <div className="flex flex-col items-center justify-center gap-8 bg-[#faf8f5] px-4 py-12">
        <div className="lg:hidden"><Logo /></div>
        {children}
      </div>
    </div>
  );
}
