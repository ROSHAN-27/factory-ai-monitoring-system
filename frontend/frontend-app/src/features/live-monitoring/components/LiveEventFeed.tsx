import { useMemo, useRef } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import { EmptyState } from "../../../shared/ui/EmptyState";
import { formatTime } from "../../../shared/lib/date";
import type { RecognitionEvent } from "../../../shared/types/domain";

export function LiveEventFeed({ events }: { events: RecognitionEvent[] }) {
  const parentRef = useRef<HTMLDivElement | null>(null);
  const visibleEvents = useMemo(() => events.slice(0, 200), [events]);
  const rowVirtualizer = useVirtualizer({
    count: visibleEvents.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 74,
    overscan: 8
  });

  if (visibleEvents.length === 0) {
    return <EmptyState title="No recognition events yet" message="Events will appear when the backend returns attendance rows or WebSocket messages." />;
  }

  return (
    <div ref={parentRef} className="h-[420px] overflow-auto pr-2">
      <div className="relative" style={{ height: rowVirtualizer.getTotalSize() }}>
        {rowVirtualizer.getVirtualItems().map((virtualRow) => {
          const event = visibleEvents[virtualRow.index];
          const isIn = event.direction === "IN";

          return (
            <div
              key={event.id}
              className="absolute left-0 top-0 w-full"
              style={{ transform: `translateY(${virtualRow.start}px)` }}
            >
              <div className="mb-2 grid grid-cols-[auto_1fr_auto] items-center gap-3 rounded-lg border border-white/8 bg-white/[0.035] p-3">
                <div className={isIn ? "text-signal-green" : "text-signal-amber"}>
                  {isIn ? <ArrowUpRight className="h-5 w-5" /> : <ArrowDownRight className="h-5 w-5" />}
                </div>
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="truncate font-medium text-white">{event.operatorName}</p>
                    <span className="rounded bg-white/8 px-1.5 py-0.5 text-[11px] text-slate-300">{event.direction}</span>
                  </div>
                  <p className="truncate text-xs text-slate-400">
                    {event.cameraName} / {event.zone} / {(event.confidence * 100).toFixed(0)}%
                  </p>
                </div>
                <time className="text-xs text-slate-500">{formatTime(event.timestamp)}</time>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
