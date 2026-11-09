import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export const Step = ({ n, title, children, hint }) => (
  <section className="space-y-3 border-b border-[#efe9df] px-6 py-6 last:border-0">
    <div className="flex items-baseline gap-3">
      <span className="font-display text-lg italic text-[#a8822e]">{String(n).padStart(2, "0")}</span>
      <h3 className="text-sm font-semibold uppercase tracking-[0.14em] text-[#1c1917]">{title}</h3>
    </div>
    {hint && <p className="text-xs text-[#78716c]">{hint}</p>}
    {children}
  </section>
);

export const Chips = ({ options = [], value, onChange, testid }) => (
  <div className="flex flex-wrap gap-2" data-testid={testid}>
    {options.map((o) => (
      <button key={o.id} type="button" data-testid={`${testid}-${o.id}`} onClick={() => onChange(o.id)}
        className={`rounded-full border px-3.5 py-1.5 text-xs transition-colors ${
          value === o.id ? "border-[#1c1917] bg-[#1c1917] text-[#faf8f5]" : "border-[#e0d8ca] bg-white text-[#44403c] hover:border-[#c9a24b]"}`}>
        {o.label}
      </button>
    ))}
  </div>
);

export const Swatches = ({ options = [], value, onChange, testid }) => (
  <div className="grid grid-cols-3 gap-2.5" data-testid={testid}>
    {options.map((o) => (
      <button key={o.id} type="button" data-testid={`${testid}-${o.id}`} onClick={() => onChange(o.id)}
        className={`group overflow-hidden rounded-md border text-left transition-shadow ${
          value === o.id ? "border-[#c9a24b] ring-2 ring-[#c9a24b]/40" : "border-[#e4ded4] hover:shadow-md"}`}>
        <div className="relative h-14" style={{ background: o.swatch?.[0] }}>
          <div className="absolute inset-y-0 right-0 w-1/3" style={{ background: o.swatch?.[1] }} />
        </div>
        <div className="bg-white px-2 py-1.5 text-[11px] font-medium leading-tight text-[#1c1917]">{o.label}</div>
      </button>
    ))}
  </div>
);

export const Field = ({ label, value, onChange, options = [], testid }) => (
  <div className="space-y-1.5">
    <label className="text-xs font-medium text-[#57534e]">{label}</label>
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger data-testid={testid} className="h-10 bg-white"><SelectValue /></SelectTrigger>
      <SelectContent>
        {options.map((o) => <SelectItem key={o.id} value={o.id} data-testid={`${testid}-opt-${o.id}`}>{o.label}</SelectItem>)}
      </SelectContent>
    </Select>
  </div>
);

export const Counter = ({ value, onChange, max = 4, testid }) => (
  <div className="flex gap-2" data-testid={testid}>
    {Array.from({ length: max }, (_, i) => i + 1).map((n) => (
      <button key={n} type="button" data-testid={`${testid}-${n}`} onClick={() => onChange(n)}
        className={`h-10 w-10 rounded-md border text-sm transition-colors ${
          value === n ? "border-[#1c1917] bg-[#1c1917] text-white" : "border-[#e0d8ca] bg-white hover:border-[#c9a24b]"}`}>{n}</button>
    ))}
  </div>
);
