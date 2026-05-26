import type { ReactNode } from "react";
import { cn } from "../lib/cn";

type PanelProps = {
  title?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
};

export function Panel({ title, action, children, className }: PanelProps) {
  return (
    <section className={cn("rounded-lg border border-white/10 bg-industrial-900/80 shadow-glow", className)}>
      {(title || action) && (
        <div className="flex items-center justify-between gap-3 border-b border-white/8 px-4 py-3">
          {title ? <h2 className="text-sm font-semibold text-white">{title}</h2> : <span />}
          {action}
        </div>
      )}
      <div className="p-4">{children}</div>
    </section>
  );
}
