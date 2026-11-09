export const PageHeader = ({ eyebrow, title, subtitle, actions }) => (
  <div className="flex flex-col gap-4 border-b border-[#ebe5da] px-6 py-8 sm:flex-row sm:items-end sm:justify-between lg:px-10">
    <div className="rise">
      {eyebrow && <p className="eyebrow">{eyebrow}</p>}
      <h1 className="mt-2 font-display text-4xl font-medium text-[#1c1917] sm:text-5xl">{title}</h1>
      {subtitle && <p className="mt-2 max-w-2xl text-sm text-[#57534e] sm:text-base">{subtitle}</p>}
    </div>
    {actions && <div className="flex flex-wrap gap-2">{actions}</div>}
  </div>
);

export const EmptyState = ({ icon: Icon, title, text, action, testid }) => (
  <div data-testid={testid} className="flex flex-col items-start gap-3 rounded-lg border border-dashed border-[#ddd3c2] bg-white/60 p-10">
    {Icon && <Icon className="h-6 w-6 text-[#a8822e]" strokeWidth={1.5} />}
    <h3 className="font-display text-2xl text-[#1c1917]">{title}</h3>
    {text && <p className="max-w-md text-sm text-[#78716c]">{text}</p>}
    {action}
  </div>
);
