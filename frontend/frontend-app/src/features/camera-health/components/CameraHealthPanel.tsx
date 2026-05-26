import { Camera, CheckCircle2, CircleAlert } from "lucide-react";
import type { CameraHealth } from "../../../shared/types/domain";
import { cn } from "../../../shared/lib/cn";

export function CameraHealthPanel({ cameras }: { cameras: CameraHealth[] }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
      {cameras.map((camera) => {
        const healthy = camera.status === "online";
        return (
          <div key={camera.id} className="rounded-lg border border-white/8 bg-white/[0.035] p-3">
            <div className="flex items-start justify-between gap-3">
              <div className="flex min-w-0 items-center gap-3">
                <Camera className="h-5 w-5 shrink-0 text-signal-cyan" />
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-white">{camera.name}</p>
                  <p className="truncate text-xs text-slate-500">{camera.zone}</p>
                </div>
              </div>
              {healthy ? <CheckCircle2 className="h-4 w-4 text-signal-green" /> : <CircleAlert className="h-4 w-4 text-signal-amber" />}
            </div>
            <div className="mt-4 grid grid-cols-3 gap-2 text-xs">
              <Metric label="FPS" value={camera.fps} tone="text-signal-cyan" />
              <Metric label="Beat" value={`${camera.heartbeatSecondsAgo}s`} tone="text-slate-300" />
              <Metric label="Acc" value={`${camera.accuracy}%`} tone={healthy ? "text-signal-green" : "text-signal-amber"} />
            </div>
          </div>
        );
      })}
    </div>
  );
}

function Metric({ label, value, tone }: { label: string; value: string | number; tone: string }) {
  return (
    <div className="rounded-md bg-black/20 p-2">
      <p className="text-slate-500">{label}</p>
      <p className={cn("mt-1 font-semibold", tone)}>{value}</p>
    </div>
  );
}
