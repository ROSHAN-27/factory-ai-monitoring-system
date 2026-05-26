import { LiveEventFeed } from "../../features/live-monitoring/components/LiveEventFeed";
import { WidgetFrame } from "../../shared/layouts/WidgetFrame";
import type { RecognitionEvent } from "../../shared/types/domain";

export function LiveFeedWidget({ events }: { events: RecognitionEvent[] }) {
  return (
    <WidgetFrame title="Live Monitoring">
      <LiveEventFeed events={events} />
    </WidgetFrame>
  );
}
