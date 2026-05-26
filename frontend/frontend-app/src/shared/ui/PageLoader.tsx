export function PageLoader({ label }: { label: string }) {
  return (
    <div className="grid min-h-[50vh] place-items-center text-sm text-slate-400">
      <div className="rounded-lg border border-white/10 bg-white/5 px-4 py-3">{label}</div>
    </div>
  );
}
