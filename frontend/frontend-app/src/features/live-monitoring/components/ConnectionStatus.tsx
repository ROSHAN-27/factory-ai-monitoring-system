import { Wifi, WifiOff } from "lucide-react";
import { useLiveMonitoringStore } from "../../../app/store/liveMonitoringStore";
import { cn } from "../../../shared/lib/cn";

export function ConnectionStatus() {
  const state = useLiveMonitoringStore((store) => store.connectionState);
  const connected = state === "connected";

  return (
    <div
      className={cn(
        "inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-xs font-semibold",
        connected
          ? "border-signal-green/30 bg-signal-green/10 text-green-100"
          : "border-signal-amber/30 bg-signal-amber/10 text-amber-100"
      )}
    >
      {connected ? <Wifi className="h-4 w-4" /> : <WifiOff className="h-4 w-4" />}
      {connected ? "Realtime connected" : state === "connecting" ? "Connecting" : "Polling fallback"}
    </div>
  );
}
